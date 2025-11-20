from copy import deepcopy
from typing import Dict, Tuple

from baton._baton._baton_runner import BatonBinary, BatonRunner
from baton._baton._constants import BATON_COLLECTION_PROPERTY, IRODS_SPECIFIC_QUERY_FIND_QUERY_BY_ALIAS, \
    BATON_SPECIFIC_QUERY_SQL_PROPERTY
from baton._baton._constants import BATON_DATA_OBJECT_PROPERTY
from baton.collections import IrodsMetadata
from baton.models import Collection, SpecificQuery, DataObject
from baton.tests._baton._helpers import create_data_object, create_collection
from testwithbaton.api import TestWithBaton

_data_object = None
_data_object_as_json = None

_collection = None
_collection_as_json = None

_specific_query = None
_specific_query_as_json = None


def create_data_object_with_baton_json_representation() -> Tuple[DataObject, Dict]:
    """
    Creates a data object and returns it along with the JSON representation of it given by baton.

    Uses baton to get the JSON representation on the first use: the JSON is retrieved from a cache in subsequent uses.
    :return: a tuple where the first element is the created data object and the second is its JSON representation
    according to baton
    """
    global _data_object, _data_object_as_json

    # Starting baton is expensive - get view of baton JSON and cache
    if _data_object is None:
        test_with_baton = TestWithBaton()
        test_with_baton.setup()

        metadata = IrodsMetadata({"attribute_a": {"value_1", "value_2"}, "attribute_b": {"value_3"}})
        _data_object = create_data_object(test_with_baton, "data_object_name", metadata)

        baton_query = {
            BATON_COLLECTION_PROPERTY: _data_object.get_collection_path(),
            BATON_DATA_OBJECT_PROPERTY: _data_object.get_name()
        }
        baton_runner = BatonRunner(test_with_baton.baton_location, test_with_baton.irods_server.users[0].zone)

        _data_object_as_json = baton_runner.run_baton_query(
                BatonBinary.BATON_LIST, ["--acl", "--avu", "--replicate", "--timestamp"], input_data=baton_query)[0]

    return deepcopy(_data_object), deepcopy(_data_object_as_json)


def create_collection_with_baton_json_representation() -> Tuple[Collection, Dict]:
    """
    Creates a collection and returns it along with the JSON representation of it given by baton.

    Uses baton to get the JSON representation on the first use: the JSON is retrieved from a cache in subsequent uses.
    :return: a tuple where the first element is the created collection and the second is its JSON representation
    according to baton
    """
    global _collection, _collection_as_json

    # Starting baton is expensive - get view of baton JSON and cache
    if _collection is None:
        test_with_baton = TestWithBaton()
        test_with_baton.setup()

        metadata = IrodsMetadata({"attribute_a": {"value_1", "value_2"}, "attribute_b": {"value_3"}})
        _collection = create_collection(test_with_baton, "collection_1", metadata)

        baton_query = {
            BATON_COLLECTION_PROPERTY: _collection.path
        }
        baton_runner = BatonRunner(test_with_baton.baton_location, test_with_baton.irods_server.users[0].zone)

        _collection_as_json = baton_runner.run_baton_query(
                BatonBinary.BATON_LIST, ["--acl", "--avu"], input_data=baton_query)[0]

    return deepcopy(_collection), deepcopy(_collection_as_json)


def create_specific_query_with_baton_json_representation() -> Tuple[SpecificQuery, Dict]:
    """
    Creates a specific query and returns it along with the JSON representation of it given by baton.

    Uses baton to get the JSON representation on the first use: the JSON is retrieved from a cache in subsequent uses.
    :return: a tuple where the first element is the created specific query and the second is its JSON representation
    according to baton
    """
    global _specific_query, _specific_query_as_json

    # Starting baton is expensive - get view of baton JSON and cache
    if _specific_query is None:
        test_with_baton = TestWithBaton()
        test_with_baton.setup()

        baton_runner = BatonRunner(test_with_baton.baton_location, test_with_baton.irods_server.users[0].zone)

        baton_query = baton_runner.run_baton_query(BatonBinary.BATON, ["-s", IRODS_SPECIFIC_QUERY_FIND_QUERY_BY_ALIAS,
                                                                       "-b", IRODS_SPECIFIC_QUERY_FIND_QUERY_BY_ALIAS])
        _specific_query_as_json = baton_runner.run_baton_query(
                BatonBinary.BATON_SPECIFIC_QUERY, input_data=baton_query)[0]

        _specific_query = SpecificQuery(
            IRODS_SPECIFIC_QUERY_FIND_QUERY_BY_ALIAS, _specific_query_as_json[0][BATON_SPECIFIC_QUERY_SQL_PROPERTY])

    return deepcopy(_specific_query), deepcopy(_specific_query_as_json)
