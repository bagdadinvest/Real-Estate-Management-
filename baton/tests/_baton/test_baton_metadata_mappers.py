import unittest
from abc import abstractmethod
from copy import deepcopy
from typing import List

from baton._baton.baton_metadata_mappers import BatonDataObjectIrodsMetadataMapper, \
    BatonCollectionIrodsMetadataMapper, _BatonIrodsMetadataMapper
from baton.collections import IrodsMetadata
from baton.models import Collection, IrodsEntity
from baton.models import DataObject
from baton.tests._baton._helpers import NAMES, create_collection, create_data_object
from baton.tests._baton._settings import BATON_SETUP
from testwithbaton.api import TestWithBaton
from testwithirods.helpers import SetupHelper


class _TestBatonIrodsEntityMetadataMapper(unittest.TestCase):
    """
    Tests for `_BatonIrodsMetadataMapper`.
    """
    @abstractmethod
    def create_mapper(self) -> _BatonIrodsMetadataMapper:
        """
        Creates a mapper to test with.
        :return: the created mapper
        """

    @abstractmethod
    def create_irods_entity(self, name: str, metadata: IrodsMetadata=IrodsMetadata()) -> IrodsEntity:
        """
        Creates an iRODS entity to test with
        :param name: the name of the entity to create
        :param metadata: the metadata to give to the entity
        :return: the created entity
        """

    def setUp(self):
        self.test_with_baton = TestWithBaton(baton_setup=BATON_SETUP)
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)
        self.mapper = self.create_mapper()
        self.metadata = IrodsMetadata({"key_1": {"value_1", "value_2"}, "key_2": {"value_3"}})
        self._entity = None
        self._entities = None

    def tearDown(self):
        self.test_with_baton.tear_down()

    @property
    def entity(self) -> IrodsEntity:
        """
        Lazily creates the test entity (prevents spending time creating unused entities in iRODS).
        :return: an example entity
        """
        if self._entity is None:
            self._entity = self.create_irods_entity("%s_entity" % NAMES[0])
        return self._entity

    @property
    def entities(self) -> List[IrodsEntity]:
        """
        Lazily creates a set of test entities (prevents spending time creating unused entities in iRODS).
        :return: an example collection of entities
        """
        if self._entities is None:
            self._entities = [self.create_irods_entity(name) for name in NAMES]
        return self._entities

    def test_get_all_with_no_paths(self):
        self.assertEqual(self.mapper.get_all([]), [])

    def test_get_all_with_single_path_that_is_invalid(self):
        self.assertRaises(FileNotFoundError, self.mapper.get_all, "/invalid")

    def test_get_all_with_single_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_get_all_with_multiple_paths_including_an_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.get_all, [self.entity.path, "/invalid"])

    def test_get_all_with_multiple_paths(self):
        entities = [self.create_irods_entity(name, self.metadata) for name in NAMES]
        paths = [entity.path for entity in entities]
        self.assertEqual(self.mapper.get_all(paths), [entity.metadata for entity in entities])

    def test_add_with_single_path_that_is_invalid(self):
        self.assertRaises(FileNotFoundError, self.mapper.add, "/invalid", self.metadata)

    def test_add_with_single_path(self):
        self.mapper.add(self.entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(self.entity.path), self.metadata)

    def test_add_with_multiple_paths_including_an_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.add, [self.entity.path, "/invalid"], self.metadata)

    def test_add_with_multiple_paths_but_invalid_number_of_associated_metadata(self):
        paths = [entity.path for entity in self.entities]
        assert len(paths) > 2
        self.assertRaises(ValueError, self.mapper.add, paths, [self.metadata, self.metadata])

    def test_add_with_multiple_paths_and_single_metadata(self):
        paths = [entity.path for entity in self.entities]
        self.mapper.add(paths, self.metadata)
        self.assertEqual(self.mapper.get_all(paths), [self.metadata for _ in self.entities])

    def test_add_with_multiple_paths_and_multiple_metadata(self):
        paths = [entity.path for entity in self.entities]
        metadata = [self.metadata for _ in range(len(self.entities))]
        self.mapper.add(paths, metadata)
        self.assertEqual(self.mapper.get_all(paths), metadata)

    def test_add_no_metadata(self):
        self.mapper.add(self.entity.path, IrodsMetadata())
        self.assertEqual(self.mapper.get_all(self.entity.path), IrodsMetadata())

    def test_add_metadata_with_same_key(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        del self.metadata["key_1"]
        assert len(self.metadata) == 1
        self.assertRaises(KeyError, self.mapper.add, entity.path, self.metadata)

    def test_add_adds_metadata(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        additional_metadata = IrodsMetadata({"other": {"values"}})
        self.mapper.add(entity.path, additional_metadata)
        self.assertEqual(self.mapper.get_all(entity.path),
                         IrodsMetadata({**dict(entity.metadata), **dict(additional_metadata)}))

    def test_add_appends_if_key_exists_and_not_same_value(self):
        values = ["value_1", "value_2"]
        key = "key"
        entity = self.create_irods_entity(NAMES[0], IrodsMetadata({key: {values[0]}}))
        self.mapper.add(entity.path, IrodsMetadata({key: {values[1]}}))
        self.assertEqual(IrodsMetadata({key: {values[0], values[1]}}), self.mapper.get_all(entity.path))

    def test_set_with_no_paths(self):
        self.mapper.set([], self.metadata)

    def test_set_with_single_path_that_is_invalid(self):
        self.assertRaises(FileNotFoundError, self.mapper.set, "/invalid", self.metadata)

    def test_set_with_single_path(self):
        self.mapper.set(self.entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(self.entity.path), self.metadata)

    def test_set_with_multiple_paths_including_an_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.set, [self.entity.path, "/invalid"], self.metadata)

    def test_set_with_multiple_paths_and_single_metadata(self):
        paths = [entity.path for entity in self.entities]
        self.mapper.set(paths, self.metadata)
        self.assertEqual(self.mapper.get_all(paths), [self.metadata for _ in self.entities])

    def test_set_with_multiple_paths_and_multiple_metadata(self):
        paths = [entity.path for entity in self.entities]
        metadata = [self.metadata for _ in range(len(self.entities))]
        self.mapper.set(paths, metadata)
        self.assertEqual(self.mapper.get_all(paths), metadata)

    def test_set_overrides_existing_metadata(self):
        overriden_key = list(self.metadata.keys())[0]
        value = {"new_value"}
        entity_1 = self.create_irods_entity(NAMES[0], self.metadata)
        del self.metadata[overriden_key]
        entity_2 = self.create_irods_entity(NAMES[1], self.metadata)
        self.mapper.set([entity_1.path, entity_2.path], IrodsMetadata({overriden_key: value}))
        self.metadata[overriden_key] = value
        self.assertEqual(self.mapper.get_all(entity_1.path), self.metadata)
        self.assertEqual(self.mapper.get_all(entity_2.path), self.metadata)

    def test_remove_with_no_paths(self):
        self.mapper.remove([], self.metadata)

    def test_remove_with_single_path_that_is_invalid(self):
        self.assertRaises(FileNotFoundError, self.mapper.remove, "/invalid", self.metadata)

    def test_remove_with_single_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.mapper.remove(entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), IrodsMetadata())

    def test_remove_with_multiple_paths_including_an_invalid_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.assertRaises(FileNotFoundError, self.mapper.remove, [entity.path, "/invalid"], self.metadata)

    def test_remove_with_multiple_paths_and_single_metadata(self):
        entities = [self.create_irods_entity(name, self.metadata) for name in NAMES]
        paths = [entity.path for entity in entities]
        self.mapper.remove(paths, self.metadata)
        self.assertEqual(self.mapper.get_all(paths), [IrodsMetadata() for _ in paths])

    def test_remove_with_multiple_paths_and_multiple_metadata(self):
        entities = [self.create_irods_entity(name, self.metadata) for name in NAMES]
        paths = [entity.path for entity in entities]
        metadata = [entity.metadata for entity in entities]
        self.mapper.remove(paths, metadata)
        self.assertEqual(self.mapper.get_all(paths), [IrodsMetadata() for _ in paths])

    def test_remove_unset_metadata(self):
        self.assertRaises(KeyError, self.mapper.remove, self.entity.path, self.metadata)

    def test_remove_partially_unset_metadata(self):
        partial_metadata = deepcopy(self.metadata)
        del partial_metadata["key_1"]
        entity = self.create_irods_entity(NAMES[0], partial_metadata)
        self.assertRaises(KeyError, self.mapper.remove, entity.path, self.metadata)

    def test_remove_subset_of_metadata(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        assert len(self.metadata) == 2
        partial_metadata_1 = deepcopy(self.metadata)
        del partial_metadata_1["key_1"]
        partial_metadata_2 = deepcopy(self.metadata)
        del partial_metadata_2["key_2"]
        self.mapper.remove(entity.path, partial_metadata_1)
        self.assertEqual(self.mapper.get_all(entity.path), partial_metadata_2)

    def test_remove_all_with_no_paths(self):
        self.mapper.remove_all([])

    def test_remove_all_with_single_path_that_is_invalid(self):
        self.assertRaises(FileNotFoundError, self.mapper.remove_all, "/invalid")

    def test_remove_all_with_single_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.mapper.remove_all(entity.path)
        self.assertEqual(self.mapper.get_all(entity.path), IrodsMetadata())

    def test_remove_all_with_multiple_paths_including_an_invalid_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.assertRaises(FileNotFoundError, self.mapper.remove_all, [entity.path, "/invalid"])

    def test_remove_all_with_multiple_paths(self):
        entities = [self.create_irods_entity(name, self.metadata) for name in NAMES]
        paths = [entity.path for entity in entities]
        self.mapper.remove_all(paths)
        self.assertEqual(self.mapper.get_all(paths), [IrodsMetadata() for _ in range(len(entities))])


class TestBatonDataObjectMapper(_TestBatonIrodsEntityMetadataMapper):
    """
    Tests for `BatonDataObjectIrodsMetadataMapper`.
    """
    def create_mapper(self) -> BatonDataObjectIrodsMetadataMapper:
        return BatonDataObjectIrodsMetadataMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, metadata: IrodsMetadata=IrodsMetadata()) -> DataObject:
        return create_data_object(self.test_with_baton, name, metadata)


class TestBatonCollectionMapper(_TestBatonIrodsEntityMetadataMapper):
    """
    Tests for `BatonCollectionIrodsMetadataMapper`.
    """
    def create_mapper(self) -> BatonCollectionIrodsMetadataMapper:
        return BatonCollectionIrodsMetadataMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, metadata: IrodsMetadata=IrodsMetadata()) -> Collection:
        return create_collection(self.test_with_baton, name, metadata)


# Trick required to stop Python's unittest from running the abstract base classes as tests
del _TestBatonIrodsEntityMetadataMapper


if __name__ == "__main__":
    unittest.main()
