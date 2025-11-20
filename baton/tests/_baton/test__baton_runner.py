import unittest
from datetime import timedelta
from subprocess import TimeoutExpired

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton.tests._baton._settings import BATON_SETUP
from baton.tests._baton._stubs import StubBatonRunner
from testwithbaton.api import TestWithBaton

_NAMES = ["name_1", "name_2", "name_3"]
_ATTRIBUTES = ["attribute_1", "attribute_2"]
_VALUES = ["value_1", "value_2", "value_3"]
_UNUSED_VALUE = "value_4"


class TestBatonRunner(unittest.TestCase):
    """
    Tests for `_BatonRunner`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBaton(baton_setup=BATON_SETUP)

    def tearDown(self):
        self.test_with_baton.tear_down()

    def test_validate_baton_binaries_location_with_invalid_location(self):
        self.assertIsInstance(BatonRunner.validate_baton_binaries_location("invalid"), ValueError)

    def test_validate_baton_binaries_location_with_non_binaries_location(self):
        self.assertIsInstance(BatonRunner.validate_baton_binaries_location("."), ValueError)

    def test_validate_baton_binaries_location_with_binaries_location(self):
        self.test_with_baton.setup()
        self.assertIsNone(BatonRunner.validate_baton_binaries_location(self.test_with_baton.baton_location))

    def test_init_with_invalid_baton_directory(self):
        self.assertRaises(ValueError, StubBatonRunner, ".", "")

    def test_init_with_valid_baton_directory(self):
        self.test_with_baton.setup()
        StubBatonRunner(self.test_with_baton.baton_location)

    def test_run_baton_query(self):
        self.test_with_baton.setup()
        baton_runner = StubBatonRunner(self.test_with_baton.baton_location)
        baton_out_as_json = baton_runner.run_baton_query(BatonBinary.BATON)[0]
        self.assertIn("avus", baton_out_as_json)
        self.assertEquals(baton_out_as_json["avus"], [])

    def test_run_command_timeout(self):
        timeout = timedelta(microseconds=1)
        baton_runner = StubBatonRunner("", timeout_queries_after=timeout, skip_baton_binaries_validation=True)
        self.assertRaises(TimeoutExpired, baton_runner._run_command, ["sleep", "999"])


if __name__ == "__main__":
    unittest.main()
