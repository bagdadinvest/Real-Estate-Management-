import json
import unittest

from frozendict import frozendict

from baton._baton._constants import BATON_AVU_PROPERTY, BATON_ACL_PROPERTY, BATON_REPLICA_PROPERTY, \
    BATON_TIMESTAMP_PROPERTY
from baton._baton.json import DataObjectReplicaJSONEncoder, AccessControlJSONEncoder, DataObjectJSONEncoder, \
    IrodsMetadataJSONEncoder, AccessControlJSONDecoder, DataObjectReplicaJSONDecoder, IrodsMetadataJSONDecoder, \
    DataObjectJSONDecoder, DataObjectReplicaCollectionJSONEncoder, DataObjectReplicaCollectionJSONDecoder, \
    CollectionJSONEncoder, CollectionJSONDecoder
from baton.tests._baton._json_helpers import create_collection_with_baton_json_representation, \
    create_data_object_with_baton_json_representation


class TestAccessControlJSONEncoder(unittest.TestCase):
    """
    Tests for `AccessControlJSONEncoder`.
    """
    def setUp(self):
        self.data_object, self.data_object_as_json = create_data_object_with_baton_json_representation()
        self.access_control = list(self.data_object.access_controls)[0]
        self.access_control_as_json = self.data_object_as_json["access"][0]

    def test_default(self):
        encoded = AccessControlJSONEncoder().default(self.access_control)
        self.assertEqual(encoded, self.access_control_as_json)

    def test_with_json_dumps(self):
        encoded = json.dumps(self.access_control, cls=AccessControlJSONEncoder)
        self.assertEqual(json.loads(encoded), self.access_control_as_json)


class TestAccessControlJSONDecoder(unittest.TestCase):
    """
    Tests for `AccessControlJSONDecoder`.
    """
    def setUp(self):
        self.data_object, self.data_object_as_json = create_data_object_with_baton_json_representation()
        self.access_control = list(self.data_object.access_controls)[0]
        self.access_control_as_json_string = json.dumps(self.data_object_as_json["access"][0])

    def test_decode(self):
        decoded = AccessControlJSONDecoder().decode(self.access_control_as_json_string)
        self.assertEqual(decoded, self.access_control)

    def test_with_json_loads(self):
        decoded = json.loads(self.access_control_as_json_string, cls=AccessControlJSONDecoder)
        self.assertEqual(decoded, self.access_control)


class TestDataObjectReplicaJSONEncoder(unittest.TestCase):
    """
    Tests for `DataObjectReplicaJSONEncoder`.
    """
    def setUp(self):
        self.data_object, self.data_object_as_json = create_data_object_with_baton_json_representation()
        self.replica = self.data_object.replicas.get_by_number(1)
        self.replica_as_json = self.data_object_as_json["replicates"][0]
        assert self.replica_as_json["number"] == 1

    def test_default(self):
        encoded = DataObjectReplicaJSONEncoder().default(self.replica)
        self.assertEqual(encoded, self.replica_as_json)

    def test_with_json_dumps(self):
        encoded = json.dumps(self.replica, cls=DataObjectReplicaJSONEncoder)
        self.assertEqual(json.loads(encoded), self.replica_as_json)


class TestDataObjectReplicaJSONDecoder(unittest.TestCase):
    """
    Tests for `DataObjectReplicaJSONDecoder`.
    """
    def setUp(self):
        self.data_object, self.data_object_as_json = create_data_object_with_baton_json_representation()
        self.replica = self.data_object.replicas.get_by_number(1)
        self.replica_as_json_string = json.dumps(self.data_object_as_json["replicates"][0])

        # Hack to cope with https://github.com/wtsi-npg/baton/issues/146
        self.replica.created = None
        self.replica.last_modified = None

    def test_decode(self):
        decoded = DataObjectReplicaJSONDecoder().decode(self.replica_as_json_string)
        self.assertEqual(decoded, self.replica)

    def test_with_json_loads(self):
        decoded = json.loads(self.replica_as_json_string, cls=DataObjectReplicaJSONDecoder)
        self.assertEqual(decoded, self.replica)


class TestDataObjectReplicaCollectionJSONEncoder(unittest.TestCase):
    """
    Tests for `DataObjectReplicaCollectionJSONDecoder`.
    """
    def setUp(self):
        self.data_object, self.data_object_as_json = create_data_object_with_baton_json_representation()
        self.replicas = self.data_object.replicas
        self.replicas_as_json = self.data_object_as_json["replicates"]

        # Hack to cope with https://github.com/wtsi-npg/baton/issues/146
        for replica in self.replicas:
            replica.created = None
            replica.last_modified = None

    def test_default(self):
        encoded = DataObjectReplicaCollectionJSONEncoder().default(self.replicas)
        self.assertEqual(encoded, self.replicas_as_json)

    def test_with_json_dumps(self):
        encoded = json.dumps(self.replicas, cls=DataObjectReplicaCollectionJSONEncoder)
        self.assertEqual(json.loads(encoded), self.replicas_as_json)


class TestDataObjectReplicaCollectionJSONDecoder(unittest.TestCase):
    """
    Tests for `DataObjectReplicaCollectionJSONDecoder`.
    """
    def setUp(self):
        self.data_object, self.data_object_as_json = create_data_object_with_baton_json_representation()
        self.replicas = self.data_object.replicas
        self.replicas_as_json_as_string = json.dumps(self.data_object_as_json["replicates"])

        # Hack to cope with https://github.com/wtsi-npg/baton/issues/146
        for replica in self.replicas:
            replica.created = None
            replica.last_modified = None

    def test_decode(self):
        decoded = DataObjectReplicaCollectionJSONDecoder().decode(self.replicas_as_json_as_string)
        self.assertEqual(decoded, self.replicas)

    def test_with_json_loads(self):
        decoded = json.loads(self.replicas_as_json_as_string, cls=DataObjectReplicaCollectionJSONDecoder)
        self.assertEqual(decoded, self.replicas)


class TestIrodsMetadataJSONEncoder(unittest.TestCase):
    """
    Tests for `IrodsMetadataJSONEncoder`.
    """
    def setUp(self):
        self.data_object, self.data_object_as_json = create_data_object_with_baton_json_representation()
        self.metadata = self.data_object.metadata
        self.metadata_as_json= self.data_object_as_json["avus"]

    def test_default(self):
        encoded = IrodsMetadataJSONEncoder().default(self.metadata)
        self.assertCountEqual(encoded, self.metadata_as_json)

    def test_with_json_dumps(self):
        encoded = json.dumps(self.metadata, cls=IrodsMetadataJSONEncoder)
        self.assertCountEqual(json.loads(encoded), self.metadata_as_json)


class TestIrodsMetadataJSONDecoder(unittest.TestCase):
    """
    Tests for `IrodsMetadataJSONDecoder`.
    """
    def setUp(self):
        self.data_object, self.data_object_as_json = create_data_object_with_baton_json_representation()
        self.metadata = self.data_object.metadata
        self.metadata_as_json_string = json.dumps(self.data_object_as_json["avus"])

    def test_decode(self):
        decoded = IrodsMetadataJSONDecoder().decode(self.metadata_as_json_string)
        self.assertEqual(decoded, self.metadata)

    def test_with_json_loads(self):
        decoded = json.loads(self.metadata_as_json_string, cls=IrodsMetadataJSONDecoder)
        self.assertEqual(decoded, self.metadata)


class TestDataObjectJSONEncoder(unittest.TestCase):
    """
    Tests for `DataObjectJSONEncoder`.
    """
    @staticmethod
    def _fix_set_as_list_in_json_issue(data_object_as_json: dict):
        """
        Work around issue that (unordered) set is represented as (ordered) list in JSON
        :param data_object_as_json: a JSON representation of a `DataObject` instance
        """
        avus = set()
        for avu in data_object_as_json[BATON_AVU_PROPERTY]:
            # Using `frozendict` as a hashable dict
            avus.add(frozendict(avu))
        data_object_as_json[BATON_AVU_PROPERTY] = avus

    def setUp(self):
        self.data_object, self.data_object_as_json = create_data_object_with_baton_json_representation()

    def test_default(self):
        encoded = DataObjectJSONEncoder().default(self.data_object)
        self._assert_data_object_as_json_equal(encoded, self.data_object_as_json)

    def test_default_with_multiple(self):
        encoded = DataObjectJSONEncoder().default([self.data_object, self.data_object])
        for data_object in encoded:
            self._assert_data_object_as_json_equal(self.data_object_as_json, data_object)

    def test_with_json_dumps(self):
        encoded = json.dumps(self.data_object, cls=DataObjectJSONEncoder)
        self._assert_data_object_as_json_equal(json.loads(encoded), self.data_object_as_json)

    def _assert_data_object_as_json_equal(self, target: dict, actual: dict):
        """
        Assert that two JSON representations of `DataObject` instances are equal.
        :param target: the data object to check
        :param actual: the data object to check against
        """
        TestDataObjectJSONEncoder._fix_set_as_list_in_json_issue(target)
        TestDataObjectJSONEncoder._fix_set_as_list_in_json_issue(actual)
        self.assertEqual(target, actual)


class TestDataObjectJSONDecoder(unittest.TestCase):
    """
    Tests for `DataObjectJSONDecoder`.
    """
    def setUp(self):
        self.data_object, self.data_object_as_json = create_data_object_with_baton_json_representation()
        self.data_object_as_json_string = json.dumps(self.data_object_as_json)

    def test_decode_when_no_metadata(self):
        del self.data_object_as_json[BATON_AVU_PROPERTY]
        self.data_object.metadata = None
        decoded = DataObjectJSONDecoder().decode(json.dumps(self.data_object_as_json))
        self.assertEqual(decoded, self.data_object)

    def test_decode_when_no_access_controls(self):
        del self.data_object_as_json[BATON_ACL_PROPERTY]
        self.data_object.access_controls = None
        decoded = DataObjectJSONDecoder().decode(json.dumps(self.data_object_as_json))
        self.assertEqual(decoded, self.data_object)

    def test_decode_when_no_replicas(self):
        del self.data_object_as_json[BATON_REPLICA_PROPERTY]
        self.data_object.replicas = None
        decoded = DataObjectJSONDecoder().decode(json.dumps(self.data_object_as_json))
        self.assertEqual(decoded, self.data_object)

    def test_decode_when_replicas_but_no_timestamp(self):
        del self.data_object_as_json[BATON_TIMESTAMP_PROPERTY]
        for replica in self.data_object.replicas:
            replica.created = None
            replica.last_modified = None
        decoded = DataObjectJSONDecoder().decode(json.dumps(self.data_object_as_json))
        self.assertEqual(decoded, self.data_object)

    def test_decode(self):
        decoded = DataObjectJSONDecoder().decode(self.data_object_as_json_string)
        self.assertEqual(decoded, self.data_object)

    def test_decode_multiple(self):
        decoded = DataObjectJSONDecoder().decode(
            "[%s, %s]" % (self.data_object_as_json_string, self.data_object_as_json_string))
        self.assertEqual(decoded, [self.data_object, self.data_object])

    def test_with_json_loads(self):
        decoded = json.loads(self.data_object_as_json_string, cls=DataObjectJSONDecoder)
        self.assertEqual(decoded, self.data_object)


class TestCollectionJSONEncoder(unittest.TestCase):
    """
    Tests for `CollectionJSONEncoder`.
    """
    def setUp(self):
        self.collection, self.collection_as_json = create_collection_with_baton_json_representation()

    def test_default(self):
        encoded = CollectionJSONEncoder().default(self.collection)
        self.assertCountEqual(encoded, self.collection_as_json)

    def test_default_with_multiple(self):
        encoded = CollectionJSONEncoder().default([self.collection, self.collection])
        for collection_as_json in encoded:
            self.assertCountEqual(collection_as_json, self.collection_as_json)

    def test_with_json_dumps(self):
        encoded = json.dumps(self.collection_as_json, cls=CollectionJSONEncoder)
        self.assertCountEqual(json.loads(encoded), self.collection_as_json)


class TestCollectionJSONDecoder(unittest.TestCase):
    """
    Tests for `CollectionJSONDecoder`.
    """
    def setUp(self):
        self.collection, self.collection_as_json = create_collection_with_baton_json_representation()
        self.collection_as_json_string = json.dumps(self.collection_as_json)

    def test_decode_when_no_metadata(self):
        del self.collection_as_json[BATON_AVU_PROPERTY]
        self.collection.metadata = None
        decoded = CollectionJSONDecoder().decode(json.dumps(self.collection_as_json))
        self.assertEqual(decoded, self.collection)

    def test_decode_when_no_access_controls(self):
        del self.collection_as_json[BATON_ACL_PROPERTY]
        self.collection.access_controls = None
        decoded = CollectionJSONDecoder().decode(json.dumps(self.collection_as_json))
        self.assertEqual(decoded, self.collection)

    def test_decode(self):
        decoded = CollectionJSONDecoder().decode(self.collection_as_json_string)
        self.assertEqual(decoded, self.collection)

    def test_decode_multiple(self):
        decoded = CollectionJSONDecoder().decode(
            "[%s, %s]" % (self.collection_as_json_string, self.collection_as_json_string))
        self.assertEqual(decoded, [self.collection, self.collection])

    def test_with_json_loads(self):
        decoded = json.loads(self.collection_as_json_string, cls=CollectionJSONDecoder)
        self.assertEqual(decoded, self.collection)


if __name__ == "__main__":
    unittest.main()
