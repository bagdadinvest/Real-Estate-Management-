from abc import ABCMeta, abstractmethod
from typing import Dict, Iterable, Union, List, Sequence

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton._baton._constants import BATON_METAMOD_OPERATION_ADD, BATON_AVU_PROPERTY, BATON_METAMOD_OPERATION_FLAG, \
    BATON_LIST_AVU_FLAG
from baton._baton._constants import BATON_METAMOD_OPERATION_REMOVE
from baton._baton.json import DataObjectJSONEncoder, CollectionJSONEncoder, IrodsMetadataJSONDecoder
from baton.collections import IrodsMetadata
from baton.mappers import IrodsMetadataMapper
from baton.models import DataObject, Collection, IrodsEntity


class _BatonIrodsMetadataMapper(BatonRunner, IrodsMetadataMapper, metaclass=ABCMeta):
    """
    iRODS metadata mapper, implemented using baton.
    """
    _IRODS_METADATA_JSON_ENCODER = IrodsMetadataJSONDecoder()

    @abstractmethod
    def _create_entity_with_path(self, path: str) -> IrodsEntity:
        """
        Creates an entity model with the given path.
        :param path: the path the entity should have
        :return: the created entity model
        """

    @abstractmethod
    def _entity_to_baton_json(self, entity: IrodsEntity) -> Dict:
        """
        Converts an entity model to its baton JSON representation.
        :param entity: the entity to produce the JSON representation of
        :return: the JSON representation
        """

    def get_all(self, paths: Union[str, Sequence[str]]) -> Union[IrodsMetadata, List[IrodsMetadata]]:
        single_path = False
        if isinstance(paths, str):
            paths = [paths]
            single_path = True

        baton_in_json = []
        for path in paths:
            baton_in_json.append(self._path_to_baton_json(path))
        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, [BATON_LIST_AVU_FLAG], input_data=baton_in_json)
        assert len(baton_out_as_json) == len(paths)

        metadata_for_paths = []
        for entity_as_baton_json in baton_out_as_json:
            metadata_as_baton_json = entity_as_baton_json[BATON_AVU_PROPERTY]
            metadata = _BatonIrodsMetadataMapper._IRODS_METADATA_JSON_ENCODER.decode_parsed(
                metadata_as_baton_json)
            metadata_for_paths.append(metadata)

        return metadata_for_paths[0] if single_path else metadata_for_paths

    def add(self, paths: Union[str, Iterable[str]], metadata: Union[IrodsMetadata, List[IrodsMetadata]]):
        self._modify(paths, metadata, BATON_METAMOD_OPERATION_ADD)

    def set(self, paths: Union[str, Iterable[str]], metadata: Union[IrodsMetadata, List[IrodsMetadata]]):
        # baton does not support "set" natively, therefore this operation is not transactional. For discussion, see:
        # https://github.com/wtsi-npg/baton/issues/160
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(metadata, IrodsMetadata):
            metadata = [metadata for _ in paths]

        # Need to remove any existing values associated to the keys to set - annoyingly, this requires the values to be
        # known
        metadatas_to_remove = []     # type: List[IrodsMetadata]
        paths_with_metadata_to_remove = []  # type: List[str]
        existing_metadatas = self.get_all(paths)
        for i in range(len(existing_metadatas)):
            existing_metadata = existing_metadatas[i]
            keys_to_remove = set(existing_metadata.keys()).intersection(metadata[i].keys())
            metadata_to_remove = IrodsMetadata({key: existing_metadata[key] for key in keys_to_remove})
            metadatas_to_remove.append(metadata_to_remove)
            paths_with_metadata_to_remove.append(paths[i])

        assert len(metadatas_to_remove) == len(paths_with_metadata_to_remove)
        self.remove(paths_with_metadata_to_remove, metadatas_to_remove)
        self.add(paths, metadata)

    def remove(self, paths: Union[str, Iterable[str]], metadata: Union[IrodsMetadata, List[IrodsMetadata]]):
        self._modify(paths, metadata, BATON_METAMOD_OPERATION_REMOVE)

    def remove_all(self, paths: Union[str, Iterable[str]]):
        metadata_for_paths = self.get_all(paths)
        self._modify(paths, metadata_for_paths, BATON_METAMOD_OPERATION_REMOVE)

    def _modify(self, paths: Union[str, List[str]], metadata_for_paths: Union[IrodsMetadata, List[IrodsMetadata]],
                operation: str):
        """
        Modifies the metadata of the entity or entities in iRODS with the given path.
        :param path: the paths of the entity or entities to modify
        :param metadata_for_paths: the metadata to change. If only one metadata object is given, that metadata is set
        for all, else the metadata is matched against the path with the corresponding index
        :param operation: the baton operation used to modify the metadata
        """
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(metadata_for_paths, IrodsMetadata):
            metadata_for_paths = [metadata_for_paths for _ in paths]
        elif len(paths) != len(metadata_for_paths):
            raise ValueError("Metadata not supplied for all paths - either supply a single IrodsMetadata collection "
                             "to apply for all paths or supply a collection for each path")

        assert len(paths) == len(metadata_for_paths)
        baton_in_json = []
        for i in range(len(metadata_for_paths)):
            entity = self._create_entity_with_path(paths[i])
            entity.metadata = metadata_for_paths[i]
            baton_in_json.append(self._entity_to_baton_json(entity))
        arguments = [BATON_METAMOD_OPERATION_FLAG, operation]
        self.run_baton_query(BatonBinary.BATON_METAMOD, arguments, input_data=baton_in_json)

    def _path_to_baton_json(self, path: str) -> Dict:
        """
        Converts a path to the type of iRODS entity the mapper deals with, to its JSON representation.
        :param path: the path to convert
        :return: the JSON representation of the path
        """
        entity = self._create_entity_with_path(path)
        return self._entity_to_baton_json(entity)


class BatonDataObjectIrodsMetadataMapper(_BatonIrodsMetadataMapper):
    """
    iRODS data object metadata mapper, implemented using baton.
    """
    def _create_entity_with_path(self, path: str) -> DataObject:
        return DataObject(path)

    def _entity_to_baton_json(self, entity: DataObject) -> Dict:
        return DataObjectJSONEncoder().default(entity)


class BatonCollectionIrodsMetadataMapper(_BatonIrodsMetadataMapper):
    """
    iRODS collection metadata mapper, implemented using baton.
    """
    def _create_entity_with_path(self, path: str) -> DataObject:
        return Collection(path)

    def _entity_to_baton_json(self, entity: Collection) -> Dict:
        return CollectionJSONEncoder().default(entity)
