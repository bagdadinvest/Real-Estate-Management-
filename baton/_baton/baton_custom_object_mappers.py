from abc import ABCMeta, abstractmethod
from typing import Sequence

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton._baton._constants import BATON_SPECIFIC_QUERY_PROPERTY, IRODS_SPECIFIC_QUERY_LS
from baton._baton.json import PreparedSpecificQueryJSONEncoder, SpecificQueryJSONDecoder
from baton.mappers import CustomObjectMapper, SpecificQueryMapper
from baton.models import PreparedSpecificQuery, SpecificQuery
from baton.types import CustomObjectType


class BatonCustomObjectMapper(BatonRunner, CustomObjectMapper[CustomObjectType], metaclass=ABCMeta):
    """
    Mapper for custom objects, implemented using baton.
    """
    @abstractmethod
    def _object_deserialiser(self, object_as_json: dict) -> CustomObjectType:
        """
        Function used to take the JSON representation of the custom object returned by the specific query and produce a
        Python model.
        :param object_as_json: JSON representation of the custom object
        :return: Python model of the custom object
        """

    def _get_with_prepared_specific_query(self, specific_query: PreparedSpecificQuery, zone: str=None) \
            -> Sequence[CustomObjectType]:
        specific_query_as_baton_json = {
            BATON_SPECIFIC_QUERY_PROPERTY: PreparedSpecificQueryJSONEncoder().default(specific_query)
        }

        arguments = []
        if zone is not None:
            arguments.extend(["--zone", "%s" % zone])

        custom_objects_as_baton_json = self.run_baton_query(
                BatonBinary.BATON_SPECIFIC_QUERY, arguments, input_data=specific_query_as_baton_json)

        custom_objects = [self._object_deserialiser(custom_object_as_baton_json)
                          for custom_object_as_baton_json in custom_objects_as_baton_json]

        return custom_objects


class BatonSpecificQueryMapper(BatonCustomObjectMapper[SpecificQuery], SpecificQueryMapper):
    """
    Mapper for specific queries installed on iRODS, implemented using baton.
    """
    def get_all(self, zone: str=None) -> Sequence[SpecificQuery]:
        retrieve_query = PreparedSpecificQuery(IRODS_SPECIFIC_QUERY_LS)
        return self._get_with_prepared_specific_query(retrieve_query, zone)

    def _object_deserialiser(self, object_as_json: dict) -> SpecificQuery:
        return SpecificQueryJSONDecoder().decode_parsed(object_as_json)
