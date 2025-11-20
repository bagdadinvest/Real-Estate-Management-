from abc import ABCMeta
from typing import Iterable, Sequence

from dateutil.parser import parser

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton._baton.json import DataObjectJSONEncoder, CollectionJSONEncoder
from baton.collections import IrodsMetadata
from baton.models import DataObject, DataObjectReplica, AccessControl, Collection, IrodsEntity, User
from hgicommon.models import Model
from testwithbaton.api import TestWithBaton
from testwithirods.helpers import AccessLevel
from testwithirods.helpers import SetupHelper

NAMES = ["name_1", "name_2", "name_3"]
ATTRIBUTES = ["attribute_1", "attribute_2"]
VALUES = ["value_1", "value_2", "value_3"]
UNUSED_VALUE = "value_4"

_access_level_conversion = {
    AccessControl.Level.NONE: AccessLevel.NONE,
    AccessControl.Level.READ: AccessLevel.READ,
    AccessControl.Level.WRITE: AccessLevel.WRITE,
    AccessControl.Level.OWN: AccessLevel.OWN
}


def _set_access_controls(test_with_baton: TestWithBaton, path: str, access_controls: Iterable[AccessControl]):
    """
    Sets the given access controls on the entity at the given iRODS path.
    :param test_with_baton: framework to allow testing with baton
    :param path: the path of the entity
    :param access_controls: the access control list the entity should have
    """
    setup_helper = SetupHelper(test_with_baton.icommands_location)
    user = test_with_baton.irods_server.users[0]
    user_with_zone = "%s#%s" % (user.username, user.zone)
    setup_helper.set_access(user_with_zone, AccessLevel.NONE, path)
    for access_control in access_controls:
        setup_helper.set_access(str(access_control.user), _access_level_conversion[access_control.level], path)


def create_data_object(test_with_baton: TestWithBaton, name: str, metadata: IrodsMetadata=IrodsMetadata(),
                       access_controls: Iterable[AccessControl]=None) -> DataObject:
    """
    Factory method to create an iRODS data object that has metadata, an ACL and replicas. Creates in current directory.
    :param test_with_baton: framework to allow testing with baton
    :param name: the name given to the created data object
    :param metadata: the metadata to give the file
    :param access_controls: access control list that the data object should have
    :return: the created iRODS file
    """
    user = test_with_baton.irods_server.users[0]
    setup_helper = SetupHelper(test_with_baton.icommands_location)

    path = setup_helper.create_data_object(name)
    setup_helper.add_metadata_to(path, metadata)
    checksum = setup_helper.get_checksum(path)
    replicas = []
    for i in range(2):
        replica_storage = setup_helper.create_replica_storage()
        setup_helper.replicate_data_object(path, replica_storage)
        replica = DataObjectReplica(i + 1, checksum, replica_storage.host, replica_storage.name, True)
        replicas.append(replica)
    setup_helper.update_checksums(path)

    # Difficult to get all the details of replica 0 using icommands so remove
    setup_helper.run_icommand(["irm", "-n", "0", path])

    if access_controls is None:
        access_controls = [AccessControl(User(user.username, user.zone), AccessControl.Level.OWN)]
    else:
        _set_access_controls(test_with_baton, path, access_controls)

    data_object = DataObject(path, access_controls, metadata, replicas)
    synchronise_timestamps(test_with_baton, data_object)

    return data_object


def create_collection(test_with_baton: TestWithBaton, name: str, metadata: IrodsMetadata=IrodsMetadata(),
                      access_controls: Iterable[AccessControl] = None) -> Collection:
    """
    Factory method to create an iRODS collection that has metadata and an ACL. Creates in current directory.
    :param test_with_baton: framework to allow testing with baton
    :param name: the name given to the created collection
    :param metadata: the metadata to give the file
    :param access_controls: access control list that the collection should have
    :return: the created iRODS file
    """
    user = test_with_baton.irods_server.users[0]
    setup_helper = SetupHelper(test_with_baton.icommands_location)

    path = setup_helper.create_collection(name)

    setup_helper.add_metadata_to(path, metadata)

    if access_controls is None:
        access_controls = [AccessControl(User(user.username, user.zone), AccessControl.Level.OWN)]
    else:
        _set_access_controls(test_with_baton, path, access_controls)

    collection = Collection(path=path, access_controls=access_controls, metadata=metadata)
    synchronise_timestamps(test_with_baton, collection)

    return collection


def synchronise_timestamps(test_with_baton: TestWithBaton, irods_entity: IrodsEntity):
    """
    Synchronises the timestamps of the given entity to align with the timestamps recorded on iRODS.
    :param test_with_baton: framework to allow testing with baton
    :param irods_entity: entity to synchronise timestamps for
    """
    if type(irods_entity) == DataObject:
        synchronise_data_object_timestamps(test_with_baton, irods_entity)
    elif type(irods_entity) == Collection:
        synchronise_collection_timestamps(test_with_baton, irods_entity)
    else:
        raise ValueError("Unsupported type: `%s`" % type(irods_entity))


def synchronise_data_object_timestamps(test_with_baton: TestWithBaton, data_object: DataObject):
    """
    Synchronises the timestamps of the given data object to align with the timestamps recorded on iRODS.
    :param test_with_baton: framework to allow testing with baton
    :param data_object: data object to synchronise timestamps for
    """
    baton_runner = BatonRunner(test_with_baton.baton_location)
    query_input = DataObjectJSONEncoder().default(data_object)
    query_return = baton_runner.run_baton_query(BatonBinary.BATON_LIST, ["--timestamp"], query_input)
    date_parser = parser()
    for timestamp_as_json in query_return[0]["timestamps"]:
        replica_number = timestamp_as_json["replicates"]
        replica = data_object.replicas.get_by_number(replica_number)
        if "created" in timestamp_as_json:
            replica.created = date_parser.parse(timestamp_as_json["created"])
        else:
            replica.last_modified = date_parser.parse(timestamp_as_json["modified"])


def synchronise_collection_timestamps(test_with_baton: TestWithBaton, collection: Collection):
    """
    Synchronises the timestamps of the given data object to align with the timestamps recorded on iRODS.
    :param test_with_baton: framework to allow testing with baton
    :param data_object: data object to synchronise timestamps for
    """
    baton_runner = BatonRunner(test_with_baton.baton_location)
    query_input = CollectionJSONEncoder().default(collection)
    query_return = baton_runner.run_baton_query(BatonBinary.BATON_LIST, ["--timestamp"], query_input)
    date_parser = parser()
    for timestamp_as_json in query_return[0]["timestamps"]:
        if "created" in timestamp_as_json:
            collection.created = date_parser.parse(timestamp_as_json["created"])
        else:
            collection.last_modified = date_parser.parse(timestamp_as_json["modified"])


def combine_metadata(metadata_collection: Iterable[IrodsMetadata]) -> IrodsMetadata:
    """
    Combines n metadata objects into a single metadata object. Key values are merged, duplicate values are removed.
    :param metadata_collection: the collection of metadata to combine
    :return: the combined metadata
    """
    combined = IrodsMetadata()
    for metadata in metadata_collection:
        for key, values in metadata.items():
            for value in values:
                combined.add(key, value)
    return combined


class EntityNode(Model, metaclass=ABCMeta):
    """
    Represents an entity in a entity tree.
    """
    def __init__(self, name: str):
        self.name = name


class CollectionNode(EntityNode):
    """
    Represents a collection in a entity tree.
    """
    def __init__(self, name: str, children: Iterable=()):
        super().__init__(name)
        self.children = children

    def get_all_descendants(self) -> Sequence[EntityNode]:
        """
        Gets all descendants of the collection node.
        """
        descendants = []
        for child in self.children:
            descendants.append(child)
            if isinstance(child, CollectionNode):
                descendants.extend(child.get_all_descendants())
        return descendants


class DataObjectNode(EntityNode):
    """
    Represents a Data Object node in a entity tree.
    """


def create_entity_tree(test_with_baton: TestWithBaton, root: str, node: EntityNode,
                       access_controls: Iterable[AccessControl]=None) -> Iterable[IrodsEntity]:
    """
    TODO
    :param test_with_baton:
    :param root:
    :param node:
    :param access_controls:
    :return:
    """
    entities = []
    setup_helper = SetupHelper(test_with_baton.icommands_location)

    if isinstance(node, DataObjectNode):
        entity = DataObject(setup_helper.create_data_object(node.name))
    else:
        entity = Collection(setup_helper.create_collection(node.name))

    _set_access_controls(test_with_baton, entity.path, access_controls)
    entity.access_controls = access_controls

    new_path = "%s/%s" % (root, entity.get_name())
    setup_helper.run_icommand(["imv", entity.path, new_path])
    entity.path = new_path
    entities.append(entity)

    if isinstance(node, CollectionNode):
        for child in node.children:
            descendants = create_entity_tree(test_with_baton, "%s/%s" % (root, node.name), child, access_controls)
            entities.extend(descendants)

    if isinstance(node, CollectionNode):
        assert len(entities) == len(list(node.get_all_descendants()) + [node])
    else:
        assert len(entities) == 1
    return entities
