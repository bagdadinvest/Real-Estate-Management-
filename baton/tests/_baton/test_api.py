import unittest
from unittest.mock import patch, MagicMock

from baton._baton.api import Connection, connect_to_irods_with_baton
from baton._baton.baton_custom_object_mappers import BatonSpecificQueryMapper
from baton._baton.baton_entity_mappers import BatonCollectionMapper, BatonDataObjectMapper
from baton.tests._baton._settings import BATON_SETUP
from testwithbaton.api import TestWithBaton


class TestConnection(unittest.TestCase):
    """
    Tests for `Connection` class.
    """
    def setUp(self):
        self.test_with_baton = TestWithBaton(baton_setup=BATON_SETUP)

    def test_correct_mapper_properties(self):
        self.test_with_baton.setup()
        connection = Connection(self.test_with_baton.baton_location)

        self.assertIsInstance(connection.data_object, BatonDataObjectMapper)
        self.assertIsInstance(connection.collection, BatonCollectionMapper)
        self.assertIsInstance(connection.specific_query, BatonSpecificQueryMapper)

    def test_skip_baton_binaries_validation(self):
        self.assertRaises(ValueError, Connection, "invalid", False)

    def tearDown(self):
        self.test_with_baton.tear_down()


class TestConnectToIrodsWithBaton(unittest.TestCase):
    """
    Tests for `connect_to_irods_with_baton` method.
    """
    @patch("baton.api.Connection.__init__", MagicMock(return_value=None))
    def test_argument_passing(self):
        baton_binaries_directory = "location"
        skip_baton_binaries_validation = True
        connection = connect_to_irods_with_baton(baton_binaries_directory, skip_baton_binaries_validation)
        connection.__init__.assert_called_with(baton_binaries_directory, skip_baton_binaries_validation)

    def test_connection_returned(self):
        connection = connect_to_irods_with_baton("somewhere", skip_baton_binaries_validation=True)
        self.assertIsInstance(connection, Connection)


if __name__ == "__main__":
    unittest.main()
