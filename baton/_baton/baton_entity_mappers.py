import collections
from abc import ABCMeta, abstractmethod
from typing import List, Union, Iterable, Sequence, Dict

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton._baton._constants import BATON_AVU_PROPERTY, BATON_COLLECTION_CONTENTS, BATON_DATA_OBJECT_PROPERTY
from baton._baton.baton_access_control_mappers import BatonDataObjectAccessControlMapper
from baton._baton.baton_metadata_mappers import BatonDataObjectIrodsMetadataMapper, BatonCollectionIrodsMetadataMapper
from baton._baton.json import SearchCriterionJSONEncoder, CollectionJSONEncoder, DataObjectJSONEncoder, \
    DataObjectJSONDecoder, CollectionJSONDecoder
from baton.mappers import IrodsEntityMapper, IrodsMetadataMapper, DataObjectMapper, CollectionMapper, \
    AccessControlMapper
from baton.models import SearchCriterion, Collection, DataObject
from baton.types import EntityType


class _BatonIrodsEntityMapper(BatonRunner, IrodsEntityMapper, metaclass=ABCMeta):
    """
    Mapper for iRODS entities, implemented using baton.
    """
    @abstractmethod
    def _path_to_baton_json(self, path: str) -> Dict:
        """
        Converts a path to the type of iRODS entity the mapper deals with, to its JSON representation.
        :param path: the path to convert
        :return: the JSON representation of the path
        """

    @abstractmethod
    def _baton_json_to_irods_entity(self, entity_as_baton_json: Dict) -> EntityType:
        """
        Converts the baton representation of an iRODS entity to a list of `EntityType` models.
        :param entity_as_baton_json: the baton serialization representation of the entity
        :return: the equivalent models
        """

    @abstractmethod
    def _extract_irods_entities_of_entity_type_from_baton_json(self, entities_as_baton_json: List[Dict]) -> List[Dict]:
        """
        Extract from the list the JSON representation of entities of type `EntityType`.
        :param entities_as_baton_json: iRODS entities encoded as baton JSON
        :return: extracted entities as baton JSON
        """

    def __init__(self, additional_metadata_query_arguments: List[str], *args, **kwargs):
        """
        Constructor.
        :param additional_metadata_query_arguments: TODO
        """
        super().__init__(*args, **kwargs)
        self._additional_metadata_query_arguments = additional_metadata_query_arguments

    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, Iterable[SearchCriterion]],
                       load_metadata: bool=True, zone: str=None) -> Sequence[EntityType]:
        if not isinstance(metadata_search_criteria, collections.Iterable):
            metadata_search_criteria = [metadata_search_criteria]

        used_attributes = dict()
        for search_criteria in metadata_search_criteria:    # type: SearchCriterion
            attribute = search_criteria.attribute
            if search_criteria.attribute in used_attributes:
                raise ValueError("baton does not allow multiple constraints on the same attribute: \"%s\"" % attribute)
            else:
                used_attributes[attribute] = True

        baton_json = {
            BATON_AVU_PROPERTY: SearchCriterionJSONEncoder().default(metadata_search_criteria)
        }
        arguments = self._create_entity_query_arguments(load_metadata)

        if zone is not None:
            arguments.append("--zone")
            arguments.append(zone)
        # Fixes #6.
        arguments.extend(self._additional_metadata_query_arguments)

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_METAQUERY, arguments, input_data=baton_json)
        return self._baton_json_to_irods_entities(baton_out_as_json)

    def get_by_path(self, paths: Union[str, Iterable[str]], load_metadata: bool=True) \
            -> Union[EntityType, Sequence[EntityType]]:
        single_path = False
        if isinstance(paths, str):
            paths = [paths]
            single_path = True
        if len(paths) == 0:
            return []

        baton_json = []
        for path in paths:
            path_json = self._path_to_baton_json(path)
            baton_json.append(path_json)
        arguments = self._create_entity_query_arguments(load_metadata)

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, arguments, input_data=baton_json)
        irods_entities = self._baton_json_to_irods_entities(baton_out_as_json)

        return irods_entities[0] if single_path else irods_entities

    def get_all_in_collection(self, collection_paths: Union[str, Iterable[str]], load_metadata: bool=True) \
            -> Sequence[EntityType]:
        if isinstance(collection_paths, str):
            collection_paths = [collection_paths]
        if len(collection_paths) == 0:
            return []

        baton_json = []
        for path in collection_paths:
            collection = Collection(path)
            collection_json = CollectionJSONEncoder().default(collection)
            baton_json.append(collection_json)
        arguments = self._create_entity_query_arguments(load_metadata)
        arguments.append("--contents")

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, arguments, input_data=baton_json)

        entities_as_baton_json = []
        for baton_item_as_json in baton_out_as_json:
            entities_as_baton_json += baton_item_as_json[BATON_COLLECTION_CONTENTS]
        data_objects_as_baton_json = self._extract_irods_entities_of_entity_type_from_baton_json(entities_as_baton_json)

        return self._baton_json_to_irods_entities(data_objects_as_baton_json)

    def _create_entity_query_arguments(self, load_metadata: bool=True) -> List[str]:
        """
        Create arguments to use with baton.
        :param load_metadata: whether baton should load metadata
        :return: the arguments to use with baton
        """
        arguments = ["--acl", "--replicate", "--timestamp"]
        if load_metadata:
            arguments.append("--avu")
        return arguments

    def _baton_json_to_irods_entities(self, entities_as_baton_json: List[Dict]) -> List[EntityType]:
        """
        Converts the baton representation of multiple iRODS entities to a list of `EntityType` models.
        :param entities_as_baton_json: the baton serialization representation of the entities
        :return: the equivalent models
        """
        assert(isinstance(entities_as_baton_json, list))

        entities = []
        for file_as_baton_json in entities_as_baton_json:
            entity = self._baton_json_to_irods_entity(file_as_baton_json)
            entities.append(entity)

        return entities


class BatonDataObjectMapper(_BatonIrodsEntityMapper, DataObjectMapper):
    """
    iRODS data object mapper, implemented using baton.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(["--obj"], *args, **kwargs)
        self._metadata_mapper = BatonDataObjectIrodsMetadataMapper(*args, **kwargs)
        self._access_control_mapper = BatonDataObjectAccessControlMapper(*args, **kwargs)

    @property
    def metadata(self) -> IrodsMetadataMapper[EntityType]:
        return self._metadata_mapper

    @property
    def access_control(self) -> AccessControlMapper:
        return self._access_control_mapper

    def _path_to_baton_json(self, path: str) -> Dict:
        data_object = DataObject(path)
        return DataObjectJSONEncoder().default(data_object)

    def _baton_json_to_irods_entity(self, entity_as_baton_json: Dict) -> DataObject:
        return DataObjectJSONDecoder().decode_parsed(entity_as_baton_json)

    def _extract_irods_entities_of_entity_type_from_baton_json(self, entities_as_baton_json: List[Dict]) -> List[Dict]:
        data_objects_as_baton_json = []
        for entity_as_baton_json in entities_as_baton_json:
            if BATON_DATA_OBJECT_PROPERTY in entity_as_baton_json:
                data_objects_as_baton_json.append(entity_as_baton_json)
        return data_objects_as_baton_json


class BatonCollectionMapper(_BatonIrodsEntityMapper, CollectionMapper):
    """
    iRODS collection mapper, implemented using baton.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(["--coll"], *args, **kwargs)
        self._metadata_mapper = BatonCollectionIrodsMetadataMapper(*args, **kwargs)
        self._access_control_mapper = BatonDataObjectAccessControlMapper(*args, **kwargs)

    @property
    def metadata(self) -> IrodsMetadataMapper[EntityType]:
        return self._metadata_mapper

    @property
    def access_control(self) -> AccessControlMapper:
        return self._access_control_mapper

    def _path_to_baton_json(self, path: str) -> Dict:
        collection = Collection(path)
        return CollectionJSONEncoder().default(collection)

    def _baton_json_to_irods_entity(self, entity_as_baton_json: Dict) -> Collection:
        return CollectionJSONDecoder().decode_parsed(entity_as_baton_json)

    def _extract_irods_entities_of_entity_type_from_baton_json(self, entities_as_baton_json: List[Dict]) -> List[Dict]:
        collections_as_baton_json = []
        for entity_as_baton_json in entities_as_baton_json:
            if BATON_DATA_OBJECT_PROPERTY not in entity_as_baton_json:
                collections_as_baton_json.append(entity_as_baton_json)
        return collections_as_baton_json
