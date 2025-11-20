import copy
import unittest

from baton.collections import DataObjectReplicaCollection, IrodsMetadata
from baton.models import DataObjectReplica


class TestIrodsMetadata(unittest.TestCase):
    """
    Tests for `IrodsMetadata`.
    """
    def setUp(self):
        self.metadata = IrodsMetadata({"attribute_a": {"value_1"}, "attribute_b": {"value_b"}})

    def test_equal(self):
        self.assertEqual(copy.deepcopy(self.metadata), self.metadata)

    def test_add_when_key_does_not_exists(self):
        self.metadata.add("key", "value")
        self.assertEqual(self.metadata["key"], {"value"})

    def test_add_when_key_exists(self):
        self.metadata["key"] = {"value_1"}
        self.metadata.add("key", "value_2")
        self.assertEqual(self.metadata["key"], {"value_1", "value_2"})

    def test_get_when_default(self):
        default = object()
        value = self.metadata.get("not_set", default=default)
        self.assertEqual(value, default)


class TestDataObjectReplicaCollection(unittest.TestCase):
    """
    Tests for `DataObjectReplicaCollection`.
    """
    def setUp(self):
        self._checksum = "1234567890"
        self._other_replica = DataObjectReplica(99, self._checksum)
        self._replicas = [DataObjectReplica(i, self._checksum, str(i), str(i), True) for i in range(10)]
        self._collection = DataObjectReplicaCollection(self._replicas)

    def test_init_with_no_initial(self):
        self.assertEqual(len(DataObjectReplicaCollection()), 0)

    def test_init_with_initial(self):
        self.assertCountEqual(self._collection, self._replicas)

    def test_get_by_number_when_does_not_exist(self):
        self.assertIsNone(self._collection.get_by_number(10))

    def test_get_by_number_when_exists(self):
        self.assertEqual(self._collection.get_by_number(0), self._replicas[0])

    def test_get_out_of_date_when_none(self):
        self.assertEqual(len(self._collection.get_out_of_date()), 0)

    def test_get_out_of_date_when_out_of_date_exist(self):
        self._replicas[1].up_to_date = False
        self._replicas[5].up_to_date = False
        self.assertCountEqual(self._collection.get_out_of_date(), [self._replicas[1], self._replicas[5]])

    def test_add_when_does_not_contain(self):
        self._collection.add(self._other_replica)
        self.assertEqual(self._collection.get_by_number(self._other_replica.number), self._other_replica)

    def test_add_when_does_contain(self):
        self.assertRaises(ValueError, self._collection.add, self._replicas[0])

    def test_remove_by_number_when_not_exists(self):
        self.assertRaises(ValueError, self._collection.remove, self._other_replica.number)

    def test_remove_by_number_when_exists(self):
        self._collection.remove(self._replicas[0].number)
        self.assertIsNone(self._collection.get_by_number(self._replicas[0].number))
        self.assertNotIn(self._replicas[0], self._collection)

    def test_remove_by_object_when_not_exists(self):
        self.assertRaises(ValueError, self._collection.remove, self._other_replica)

    def test_remove_by_object_when_exists(self):
        self._collection.remove(self._replicas[0])
        self.assertNotIn(self._replicas[0], self._collection)

    def test_remove_by_unsupported_type(self):
        self.assertRaises(TypeError, self._collection.remove, None)

    def test_eq_when_not_equal(self):
        another_collection = DataObjectReplicaCollection()
        self.assertNotEqual(another_collection, self._collection)

    def test_eq_when_equal(self):
        self.assertEqual(copy.copy(self._collection), self._collection)

    def test_len(self):
        self.assertEqual(len(self._collection), len(self._replicas))

    def test_iter(self):
        retrieved = []
        for data_object_replica in self._collection:
            retrieved.append(data_object_replica)
        self.assertCountEqual(retrieved, self._replicas)

    def test_contains(self):
        self.assertIn(self._replicas[0], self._collection)


if __name__ == "__main__":
    unittest.main()
