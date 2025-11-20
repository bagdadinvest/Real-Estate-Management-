import unittest
from typing import Sequence
from unittest.mock import MagicMock

from testwithirods.helpers import SetupHelper

from baton._baton.baton_custom_object_mappers import BatonSpecificQueryMapper
from baton.models import PreparedSpecificQuery, SpecificQuery
from baton.tests._baton._settings import BATON_SETUP
from baton.tests._baton._stubs import StubBatonCustomObjectMapper
from testwithbaton.api import TestWithBaton


class TestBatonCustomObjectMapper(unittest.TestCase):
    """
    Tests for `BatonCustomObjectMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBaton(baton_setup=BATON_SETUP)
        self.test_with_baton.setup()

        self.mapper = StubBatonCustomObjectMapper(self.test_with_baton.baton_location)
        self.mapper._object_deserialiser = MagicMock(wraps=self.mapper._object_deserialiser)

    def tearDown(self):
        self.test_with_baton.tear_down()

    def test_get_using_specific_query(self):
        results = self.mapper._get_with_prepared_specific_query(PreparedSpecificQuery("ls"))
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), self.mapper._object_deserialiser.call_count)


class TestBatonInstalledSpecificQueryMapper(unittest.TestCase):
    """
    Tests for `BatonSpecificQueryMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBaton(baton_setup=BATON_SETUP)
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)

        self.mapper = BatonSpecificQueryMapper(self.test_with_baton.baton_location)

    def test_get_all(self):
        iquest_ls_response = self.setup_helper.run_icommand(["iquest", "--sql", "ls"])
        expected = TestBatonInstalledSpecificQueryMapper._parse_iquest_ls(iquest_ls_response)
        specific_queries = self.mapper.get_all()
        self.assertCountEqual(specific_queries, expected)

    @staticmethod
    def _parse_iquest_ls(iquest_ls_response: str) -> Sequence[SpecificQuery]:
        """
        Gets the installed specific queries by parsing the output returned by "iquest --sql ls".
        :param iquest_ls_response: the response returned by the iquest command
        :return: the specific queries installed on the iRODS server
        """
        iquest_ls_response_lines = iquest_ls_response.split('\n')
        assert (len(iquest_ls_response_lines) + 1) % 3 == 0

        specific_queries = []
        for i in range(int((len(iquest_ls_response_lines) + 1) / 3)):
            i3 = int(3 * i)
            alias = iquest_ls_response_lines[i3]
            sql = iquest_ls_response_lines[i3 + 1]
            specific_queries.append(SpecificQuery(alias, sql))

        return specific_queries


if __name__ == "__main__":
    unittest.main()
