from abc import ABCMeta, abstractmethod, abstractproperty
from typing import Generic, Union, Sequence, Iterable, Set, List

from baton.collections import IrodsMetadata
from baton.models import Collection, DataObject, PreparedSpecificQuery, SpecificQuery, SearchCriterion, AccessControl, \
    User
from baton.types import EntityType, CustomObjectType


class IrodsMetadataMapper(Generic[EntityType], metaclass=ABCMeta):
    """
    iRODS metadata mapper.
    """
    @abstractmethod
    def get_all(self, paths: Union[str, Sequence[str]]) -> Union[IrodsMetadata, List[IrodsMetadata]]:
        """
        Gets all of the metadata for the iRODS entities at the given path or paths.

        If multiple paths are given, the metadata collection at index `i` on the output corresponds to the path at index
        `i` on the input. i.e.
        ```
        output = mapper.get_all(["path_1", "path_2"])
        metadata_for_path_1 = output[0]
        metadata_for_path_2 = output[1]
        ```

        A `ValueError` will be raised will be raised if the path does not correspond to a valid entity.
        :param path: the path of the entity or entities to get the metadata for
        :return: metadata for the given entity or entities
        """

    @abstractmethod
    def add(self, paths: Union[str, Iterable[str]], metadata: Union[IrodsMetadata, List[IrodsMetadata]]):
        """
        Adds the given metadata to the given iRODS entities at the given path or paths.

        If a single metadata collection is given, that metadata is added to all paths. If a list of metadata are given,
        each collection is added to the path with the corresponding index.

        A `ValueError` will be raised will be raised if the path does not correspond to a valid entity.
        :param path: the path of the entity or entities to add the metadata to
        :param metadata: the metadata to write
        """

    @abstractmethod
    def set(self, paths: Union[str, Iterable[str]], metadata: Union[IrodsMetadata, List[IrodsMetadata]]):
        """
        Sets the given metadata on the iRODS entities at the given path or paths. Similar to `add` excpet pre-existing
        metadata with matching keys will be overwritten.

        If a single metadata collection is given, that metadata is set for all paths. If a list of metadata are given,
        each collection is set for the path with the corresponding index.

        A `ValueError` will be raised will be raised if the path does not correspond to a valid entity.
        :param path: the path of the entity to set the metadata for
        :param metadata: the metadata to set
        """

    @abstractmethod
    def remove(self, paths: Union[str, Iterable[str]], metadata: Union[IrodsMetadata, List[IrodsMetadata]]):
        """
        Removes the given metadata from the given iRODS entity.

        If a single metadata collection is given, that metadata is removed from all paths. If a list of metadata are
        given, each collection is removed for the path with the corresponding index.

        A `KeyError` will be raised if the entity does not have metadata with the given key and value. If this exception
        is raised part-way through the removal of multiple pieces of metadata, a rollback will not occur - it would be
        necessary to get the metadata for the entity to determine what metadata in the collection was removed
        successfully.

        A `ValueError` will be raised will be raised if the path does not correspond to a valid entity.
        :param path: the path of the entity to remove metadata from
        :param metadata: the metadata to remove
        """

    @abstractmethod
    def remove_all(self, paths: Union[str, Iterable[str]]):
        """
        Removes all of the metadata from the given iRODS entities at the given path or paths.

        A `ValueError` will be raised will be raised if the path does not correspond to a valid entity.
        :param path: the path of the entity to remove all of the metadata from
        """


class AccessControlMapper(metaclass=ABCMeta):
    """
    Access control mapper.
    """
    @abstractmethod
    def get_all(self, paths: Union[str, Sequence[str]]) -> Union[Set[AccessControl], Sequence[Set[AccessControl]]]:
        """
        Gets all the access controls for the entity with the given path.
        :param path: the path of the entity to find access controls for
        :return:
        """

    @abstractmethod
    def add_or_replace(self, paths: Union[str, Iterable[str]],
                       access_controls: Union[AccessControl, Iterable[AccessControl]]):
        """
        Adds the given access controls to those associated with the given path or collection of paths. If an access
        control already exists for a user, the access control is replaced.
        :param paths: the paths to add the access controls
        :param access_controls: the access controls to add
        """

    @abstractmethod
    def set(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        """
        Sets the access controls associated to a give path or collection of paths to those given.
        :param paths: the paths to set the access controls for
        :param access_controls: the access controls to set
        """

    @abstractmethod
    def revoke(self, paths: Union[str, Iterable[str]], users: Union[str, Iterable[str], User, Iterable[User]]):
        """
        Revokes all access controls that are associated to the given path or collection of paths.
        :param paths: the paths to remove access controls on
        :param users: the users to revoke access controls for. User may be in the represented as a `User` object or in
        the form "name#zone"
        """

    @abstractmethod
    def revoke_all(self, paths: Union[str, Iterable[str]]):
        """
        Removes all access controls associated to the given path or collection of paths.
        :param paths: the paths to remove all access controls on (i.e. they are made accessible to no-one)
        """


class CollectionAccessControlMapper(AccessControlMapper, metaclass=ABCMeta):
    """
    Access control mapper for controls relating specifically to collections.
    """
    @abstractmethod
    def add_or_replace(self, paths: Union[str, Iterable[str]],
                       access_controls: Union[AccessControl, Iterable[AccessControl]], recursive: bool=False):
        """
        See `AccessControlMapper.add`.
        :param paths: see `AccessControlMapper.add`
        :param access_controls: see `AccessControlMapper.add`
        :param recursive: whether the access control list should be changed recursively for all nested collections
        """

    @abstractmethod
    def set(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]],
            recursive: bool=False):
        """
        See `AccessControlMapper.set`.
        :param paths: see `AccessControlMapper.set`
        :param access_controls: see `AccessControlMapper.set`
        :param recursive: whether the access control list should be changed recursively for all nested collections
        """

    @abstractmethod
    def revoke(self, paths: Union[str, Iterable[str]], users: Union[str, Iterable[str], User, Iterable[User]],
               recursive: bool=False):
        """
        See `AccessControlMapper.revoke`.
        :param paths: see `AccessControlMapper.revoke`
        :param users: see `AccessControlMapper.revoke`
        :param recursive: whether the access control list should be changed recursively for all nested collections
        """

    @abstractmethod
    def revoke_all(self, paths: Union[str, Iterable[str]], recursive: bool=False):
        """
        See `AccessControlMapper.revoke_all`.
        :param paths: see `AccessControlMapper.revoke_all`
        :param access_controls: see `AccessControlMapper.revoke_all`
        :param recursive: whether the access control list should be changed recursively for all nested collections
        """


class IrodsEntityMapper(Generic[EntityType], metaclass=ABCMeta):
    """
    iRODS entity mapper.
    """
    @abstractproperty
    def metadata(self) -> IrodsMetadataMapper[EntityType]:
        """
        Property to access a mapper for metadata that can be assocaited to the iRODS entity that this mapper deals with.
        :return: mapper for metadata
        """

    @abstractproperty
    def access_control(self) -> AccessControlMapper:
        """
        Property to access a mapper for access controls related the entities that this mapper deals with.
        :return: the entity access control mapper
        """

    @abstractmethod
    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, Iterable[SearchCriterion]],
                        load_metadata: bool=True, zone: str=None) -> Sequence[EntityType]:
        """
        Gets entities from iRODS that have metadata that matches the given search criteria.
        :param metadata_search_criteria: the metadata search criteria
        :param load_metadata: whether metadata associated to the entities should be loaded
        :param zone: limit query to specific zone in iRODS
        :return: the matched entities in iRODS
        """

    @abstractmethod
    def get_by_path(self, paths: Union[str, Iterable[str]], load_metadata: bool=True) \
            -> Union[EntityType, Sequence[EntityType]]:
        """
        Gets the entity or entities with the given path or paths from iRODS.

        If one or more of the entities does not exist, a `FileNotFound` exception will be raised.
        :param paths: the paths of the entities to get from iRODS
        :param load_metadata: whether metadata associated to the entities should be loaded
        :return: the single entity retrieved from iRODS if a single path is given, else a sequence of retrieved entities
        """

    @abstractmethod
    def get_all_in_collection(self, collection_paths: Union[str, Iterable[str]], load_metadata: bool = True) \
            -> Sequence[EntityType]:
        """
        Gets entities contained within the given iRODS collections.

        If one or more of the collection_paths does not exist, a `FileNotFound` exception will be raised.
        :param collection_paths: the collection(s) to get the entities from
        :param load_metadata: whether metadata associated to the entities should be loaded
        :return: the entities loaded from iRODS
        """


class DataObjectMapper(IrodsEntityMapper[DataObject], metaclass=ABCMeta):
    """
    iRODS data object mapper.
    """


class CollectionMapper(IrodsEntityMapper[Collection], metaclass=ABCMeta):
    """
    iRODS collection mapper.
    """
    @abstractproperty
    def access_control(self) -> CollectionAccessControlMapper:
        """
        Mapper for access controls related the the collections that this mapper deals with.
        :return: the collection access control mapper
        """


class CustomObjectMapper(Generic[CustomObjectType], metaclass=ABCMeta):
    """
    Mapper for a custom object, retrieved from iRODS using a pre-installed specific query.
    """
    @abstractmethod
    def _get_with_prepared_specific_query(self, specific_query: PreparedSpecificQuery, zone: str=None) \
            -> Sequence[CustomObjectType]:
        """
        Gets an object from iRODS using a specific query.
        :param specific_query: the specific query to use
        :param zone: limit query to specific zone in iRODS
        :return: Python model of the object returned from iRODS using the specific query
        """


class SpecificQueryMapper(CustomObjectMapper[SpecificQuery], metaclass=ABCMeta):
    """
    Mapper for specific queries installed on iRODS, implemented using baton.
    """
    @abstractmethod
    def get_all(self) -> Sequence[SpecificQuery]:
        """
        Gets all of the specific queries installed on the iRODS server.
        :return: all of the installed queries
        """
