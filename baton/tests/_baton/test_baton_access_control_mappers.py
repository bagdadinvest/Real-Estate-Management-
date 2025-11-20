import unittest
from abc import abstractmethod
from typing import Iterable, List

from testwithirods.helpers import SetupHelper

from baton._baton.baton_access_control_mappers import _BatonAccessControlMapper, BatonDataObjectAccessControlMapper, \
    BatonCollectionAccessControlMapper
from baton.models import AccessControl, DataObject, Collection, User
from baton.models import IrodsEntity
from baton.tests._baton._helpers import DataObjectNode, CollectionNode, NAMES, create_data_object, create_collection, \
    create_entity_tree, EntityNode
from baton.tests._baton._settings import BATON_SETUP
from testwithbaton.api import TestWithBaton

_USERNAMES = ["user_1", "user_2", "user_3"]

_TEST_ENTITY_TREE = CollectionNode("top", [
    CollectionNode("middle_1", [
        DataObjectNode("bottom_1a"),
        DataObjectNode("bottom_1b")
    ]),
    CollectionNode("middle_2", [
        CollectionNode("bottom_2")
    ])
])


class _TestBatonAccessControlMapper(unittest.TestCase):
    """
    Tests for `_BatonAccessControlMapper`.
    """
    @abstractmethod
    def create_mapper(self) -> _BatonAccessControlMapper:
        """
        Creates a mapper to test with.
        :return: the created mapper
        """

    @abstractmethod
    def create_irods_entity(self, name: str, access_controls: Iterable[AccessControl]) -> IrodsEntity:
        """
        Creates an iRODS entity to test with
        :param name: the name of the entity to create
        :param access_controls: the access controls the entity should have
        :return: the created entity
        """

    def setUp(self):
        self.test_with_baton = TestWithBaton(baton_setup=BATON_SETUP)
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)
        self.mapper = self.create_mapper()

        self.users = []
        for username in _USERNAMES:
            user = User(username, self.test_with_baton.irods_server.users[0].zone)
            self.setup_helper.create_user(user.name, user.zone)
            self.users.append(user)

        self.access_controls = [AccessControl(self.users[0], AccessControl.Level.WRITE),
                                AccessControl(self.users[1], AccessControl.Level.READ)]
        self.access_control = AccessControl(self.users[2], AccessControl.Level.OWN)

    def tearDown(self):
        self.test_with_baton.tear_down()

    def test_get_all_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.get_all, "/invalid")

    def test_get_all_with_no_paths(self):
        self.assertEqual(self.mapper.get_all([]), [])

    def test_get_all_with_single_path(self):
        entity = self.create_irods_entity(NAMES[0], self.access_controls)
        self.assertEqual(self.mapper.get_all(entity.path), set(self.access_controls))

    def test_get_all_with_multiple_path(self):
        entity_1 = self.create_irods_entity(NAMES[0], self.access_controls)
        entity_2 = self.create_irods_entity(NAMES[1], [self.access_control])
        entity_3 = self.create_irods_entity(NAMES[2], [])
        self.assertEqual(self.mapper.get_all([entity_1.path, entity_2.path, entity_3.path]),
                         [set(self.access_controls), {self.access_control}, set()])

    def test_add_or_replace_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.add_or_replace, "/invalid", self.access_controls)

    def test_add_or_replace_with_no_paths(self):
        self.mapper.add_or_replace([], self.access_controls[0])

    def test_add_or_replace_single_access_control(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add_or_replace(entity.path, self.access_controls[0])
        self.assertCountEqual(self.mapper.get_all(entity.path), [self.access_control, self.access_controls[0]])

    def test_add_or_replace_single_access_control_when_already_exists(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add_or_replace(entity.path, self.access_control)
        self.assertEqual(self.mapper.get_all(entity.path), {self.access_control})

    def test_add_or_replace_multiple_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add_or_replace(entity.path, self.access_controls)
        self.assertCountEqual(self.mapper.get_all(entity.path), [self.access_control] + self.access_controls)

    def test_add_or_replace_multiple_access_controls_when_one_access_control_already_exists(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add_or_replace(entity.path, self.access_controls + [self.access_control])
        self.assertEqual(self.mapper.get_all(entity.path), set(self.access_controls + [self.access_control]))

    def test_set_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.set, "/invalid", self.access_controls)

    def test_set_with_no_paths(self):
        self.mapper.set([], self.access_controls)

    def test_set_when_no_existing_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], ())
        self.mapper.set(entity.path, self.access_controls)
        self.assertEqual(self.mapper.get_all(entity.path), set(self.access_controls))

    def test_set_when_existing_non_duplicate_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.set(entity.path, self.access_controls)
        self.assertEqual(self.mapper.get_all(entity.path), set(self.access_controls))

    def test_set_when_existing_duplicate_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], self.access_controls)
        self.mapper.set(entity.path, self.access_controls)
        self.assertEqual(self.mapper.get_all(entity.path), set(self.access_controls))

    def test_revoke_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.revoke, "/invalid", self.access_control.user)

    def test_revoke_with_no_paths(self):
        self.mapper.revoke([], self.access_control.user)

    def test_revoke_unset_access_control(self):
        entity = self.create_irods_entity(NAMES[0], ())
        self.mapper.revoke(entity.path, self.access_control.user)
        self.assertEqual(self.mapper.get_all(entity.path), set())

    def test_revoke_subset_of_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], self.access_controls + [self.access_control])
        self.mapper.revoke(entity.path, [access_control.user for access_control in self.access_controls])
        self.assertEqual(self.mapper.get_all(entity.path), {self.access_control})

    def test_revoke_access_controls_using_string_representation_of_user(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.revoke(entity.path, [str(self.access_control.user)])
        self.assertEqual(self.mapper.get_all(entity.path), set())

    def test_revoke_all_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.revoke_all, "/invalid")

    def test_revoke_all_with_no_paths(self):
        self.mapper.revoke_all([])

    def test_revoke_all_with_single_path_and_no_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], ())
        self.mapper.revoke_all(entity.path)
        self.assertEqual(self.mapper.get_all(entity.path), set())

    def test_revoke_all_with_single_path(self):
        entity = self.create_irods_entity(NAMES[0], self.access_controls)
        self.mapper.revoke_all(entity.path)
        self.assertEqual(self.mapper.get_all(entity.path), set())

    def test_revoke_all_with_multiple_paths(self):
        entities = [self.create_irods_entity(name, self.access_controls) for name in NAMES]
        paths = [entity.path for entity in entities]
        self.mapper.revoke_all(paths)
        self.assertEqual(self.mapper.get_all(paths), [set() for _ in range(len(paths))])


class TestBatonDataObjectAccessControlMapper(_TestBatonAccessControlMapper):
    """
    Tests for `BatonDataObjectAccessControlMapper`.
    """
    def create_mapper(self) -> BatonDataObjectAccessControlMapper:
        return BatonDataObjectAccessControlMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, access_controls: Iterable[AccessControl]) -> DataObject:
        return create_data_object(self.test_with_baton, name, access_controls=access_controls)


class TestBatonCollectionAccessControlMapper(_TestBatonAccessControlMapper):
    """
    Tests for `BatonCollectionAccessControlMapper`.
    """
    def setUp(self):
        super().setUp()
        self.mapper = self.mapper  # type: BatonCollectionAccessControlMapper
        self._collection_count = 0
        irods_user = self.test_with_baton.irods_server.users[0]
        default_user = User(irods_user.username, irods_user.zone)
        self.access_controls.append(AccessControl(default_user, AccessControl.Level.OWN))
        self.entities, self.root_collection = self._create_entity_tree_in_container(_TEST_ENTITY_TREE)

    def create_mapper(self) -> BatonCollectionAccessControlMapper:
        return BatonCollectionAccessControlMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, access_controls: Iterable[AccessControl]) -> Collection:
        return create_collection(self.test_with_baton, name, access_controls=access_controls)

    def test_set_with_recursion_for_single_path(self):
        new_access_controls = {AccessControl(self.users[2], AccessControl.Level.WRITE)}
        self.mapper.set(self.root_collection.path, new_access_controls, recursive=True)

        access_controls_for_paths = self.mapper.get_all([entity.path for entity in self.entities])
        for access_controls in access_controls_for_paths:
            self.assertEqual(access_controls, new_access_controls)

    def test_set_with_recursion_for_multiple_paths(self):
        other_entities, other_root_collection = self._create_entity_tree_in_container(_TEST_ENTITY_TREE)
        new_access_controls = {AccessControl(self.users[2], AccessControl.Level.WRITE)}
        self.mapper.set([self.root_collection.path, other_root_collection.path], new_access_controls, recursive=True)

        access_controls_for_paths = self.mapper.get_all([entity.path for entity in self.entities + other_entities])
        for access_controls in access_controls_for_paths:
            self.assertEqual(access_controls, new_access_controls)

    def test_add_with_recursion_for_single_path(self):
        additional_access_controls = {AccessControl(self.users[2], AccessControl.Level.WRITE), self.access_controls[0]}
        self.mapper.add_or_replace(self.root_collection.path, additional_access_controls, recursive=True)

        access_controls_for_paths = self.mapper.get_all([entity.path for entity in self.entities])
        expected_access_controls = additional_access_controls.union(self.access_controls)
        for access_controls in access_controls_for_paths:
            self.assertEqual(access_controls, expected_access_controls)

    def test_add_with_recursion_for_multiple_paths(self):
        other_entities, other_root_collection = self._create_entity_tree_in_container(_TEST_ENTITY_TREE)
        additional_access_controls = [AccessControl(self.users[2], AccessControl.Level.WRITE), self.access_controls[0]]
        self.mapper.add_or_replace(
            [self.root_collection.path, other_root_collection.path], additional_access_controls, recursive=True)

        access_controls_for_paths = self.mapper.get_all([entity.path for entity in self.entities + other_entities])
        expected_access_controls = set(additional_access_controls + self.access_controls)
        for access_controls in access_controls_for_paths:
            self.assertEqual(access_controls, expected_access_controls)

    def test_revoke_with_recursion_for_single_path(self):
        self.mapper.revoke(self.root_collection.path, self.access_controls[0].user, recursive=True)

        access_controls_for_paths = self.mapper.get_all([entity.path for entity in self.entities])
        expected_access_controls = set(self.access_controls[1:])
        for access_controls in access_controls_for_paths:
            self.assertEqual(access_controls, expected_access_controls)

    def test_revoke_with_recursion_for_multiple_paths(self):
        other_entities, other_root_collection = self._create_entity_tree_in_container(_TEST_ENTITY_TREE)
        self.mapper.revoke([self.root_collection.path, other_root_collection.path],
                           self.access_controls[0].user, recursive=True)

        access_controls_for_paths = self.mapper.get_all([entity.path for entity in self.entities + other_entities])
        expected_access_controls = set(self.access_controls[1:])
        for access_controls in access_controls_for_paths:
            self.assertEqual(access_controls, expected_access_controls)

    def test_revoke_all_with_recursion_for_single_path(self):
        self.mapper.revoke_all(self.root_collection.path, recursive=True)

        access_controls_for_paths = self.mapper.get_all([entity.path for entity in self.entities])
        for access_controls in access_controls_for_paths:
            self.assertEqual(len(access_controls), 0)

    def test_revoke_all_with_recursion_for_multiple_paths(self):
        other_entities, other_root_collection = self._create_entity_tree_in_container(_TEST_ENTITY_TREE)
        self.mapper.revoke_all([self.root_collection.path, other_root_collection.path], recursive=True)

        access_controls_for_paths = self.mapper.get_all([entity.path for entity in self.entities + other_entities])
        for access_controls in access_controls_for_paths:
            self.assertEqual(len(access_controls), 0)

    def _create_entity_tree_in_container(self, entity_tree: EntityNode) -> (List[IrodsEntity], IrodsEntity):
        """
        Creates the given entity tree inside a container.
        :param entity_tree: the entity to create
        :return: tuple where the first element is a list of all the created iRODS entities (not including the container)
        and the second is the top level iRODS entity (not including the container)
        """
        self._collection_count += 1
        container_path = self.setup_helper.create_collection("container-%d" % self._collection_count)
        entities = list(create_entity_tree(self.test_with_baton, container_path, entity_tree, self.access_controls))

        for entity in entities:
            if entity.get_collection_path() == container_path:
                assert entity.get_name() == entity_tree.name
                return entities, entity

        assert False


# Trick required to stop Python's unittest from running the abstract base classes as tests
del _TestBatonAccessControlMapper


if __name__ == "__main__":
    unittest.main()
