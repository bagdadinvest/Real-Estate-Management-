import json
from json import JSONEncoder, JSONDecoder
from typing import Dict, List, Union

from dateutil.parser import parser

from baton._baton._constants import BATON_ACL_LEVELS, BATON_ACL_OWNER_PROPERTY, BATON_ACL_LEVEL_PROPERTY, \
    BATON_REPLICA_NUMBER_PROPERTY, BATON_REPLICA_VALID_PROPERTY, BATON_REPLICA_CHECKSUM_PROPERTY, \
    BATON_REPLICA_LOCATION_PROPERTY, BATON_REPLICA_RESOURCE_PROPERTY,  BATON_AVU_ATTRIBUTE_PROPERTY, \
    BATON_AVU_VALUE_PROPERTY, BATON_ACL_PROPERTY, BATON_AVU_PROPERTY, BATON_COLLECTION_PROPERTY, \
    BATON_DATA_OBJECT_PROPERTY, BATON_REPLICA_PROPERTY, BATON_SEARCH_CRITERION_ATTRIBUTE_PROPERTY, \
    BATON_SEARCH_CRITERION_VALUE_PROPERTY, BATON_SEARCH_CRITERION_COMPARISON_OPERATOR_PROPERTY, \
    BATON_SEARCH_CRITERION_COMPARISON_OPERATORS, BATON_SPECIFIC_QUERY_SQL_PROPERTY, \
    BATON_SPECIFIC_QUERY_ARGUMENTS_PROPERTY, BATON_SPECIFIC_QUERY_ALIAS_PROPERTY, BATON_ACL_ZONE_PROPERTY, \
    BATON_TIMESTAMP_LAST_MODIFIED_PROPERTY, BATON_TIMESTAMP_CREATED_PROPERTY, BATON_TIMESTAMP_PROPERTY, \
    BATON_TIMESTAMP_REPLICA_NUMBER_LINK_PROPERTY
from baton.collections import IrodsMetadata, DataObjectReplicaCollection
from baton.models import AccessControl, DataObjectReplica, DataObject, IrodsEntity, Collection, PreparedSpecificQuery, \
    SpecificQuery, SearchCriterion
from hgicommon.enums import ComparisonOperator
from hgijson.json.builders import MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder, \
    SetJSONEncoderClassBuilder, SetJSONDecoderClassBuilder
from hgijson.json.interfaces import ParsedJSONDecoder
from hgijson.json.models import JsonPropertyMapping
from hgijson.types import PrimitiveJsonSerializableType


# JSON encoder/decoder for `AccessControl`
def _access_control_level_to_string(level: AccessControl.Level):
    assert level in BATON_ACL_LEVELS
    return BATON_ACL_LEVELS[level]

def _access_control_level_from_string(level_as_string: str):
    return [key for key, value in BATON_ACL_LEVELS.items() if value == level_as_string][0]

_access_control_json_mappings = [
    JsonPropertyMapping(
        None, "user", "user",
        json_property_getter=lambda json_as_dict: "%s#%s" % (json_as_dict[BATON_ACL_OWNER_PROPERTY],
                                                             json_as_dict[BATON_ACL_ZONE_PROPERTY])
    ),
    JsonPropertyMapping(BATON_ACL_OWNER_PROPERTY,
                        object_property_getter=lambda access_control: access_control.user.name),
    JsonPropertyMapping(BATON_ACL_ZONE_PROPERTY,
                        object_property_getter=lambda access_control: access_control.user.zone),
    JsonPropertyMapping(BATON_ACL_LEVEL_PROPERTY, None, "level",
                        object_property_getter=lambda access_control: _access_control_level_to_string(
                            access_control.level),
                        object_constructor_argument_modifier=lambda level_as_string: _access_control_level_from_string(
                            level_as_string))
]
AccessControlJSONEncoder = MappingJSONEncoderClassBuilder(AccessControl, _access_control_json_mappings).build()
AccessControlJSONDecoder = MappingJSONDecoderClassBuilder(AccessControl, _access_control_json_mappings).build()


# JSON encoder/decoder for sets of `AccessControl` instances
AccessControlSetJSONEncoder = SetJSONEncoderClassBuilder(AccessControlJSONEncoder).build()
AccessControlSetJSONDecoder = SetJSONDecoderClassBuilder(AccessControlJSONDecoder).build()


# JSON encoder/decoder for `DataObjectReplica`
_data_object_replica_json_mappings = [
    JsonPropertyMapping(BATON_REPLICA_NUMBER_PROPERTY, "number", "number"),
    JsonPropertyMapping(BATON_REPLICA_CHECKSUM_PROPERTY, "checksum", "checksum"),
    JsonPropertyMapping(BATON_REPLICA_LOCATION_PROPERTY, "host", "host", optional=True),
    JsonPropertyMapping(BATON_REPLICA_RESOURCE_PROPERTY, "resource_name", "resource_name", optional=True),
    JsonPropertyMapping(BATON_REPLICA_VALID_PROPERTY, "up_to_date", "up_to_date")
]
DataObjectReplicaJSONEncoder = MappingJSONEncoderClassBuilder(
    DataObjectReplica, _data_object_replica_json_mappings).build()
DataObjectReplicaJSONDecoder = MappingJSONDecoderClassBuilder(
    DataObjectReplica, _data_object_replica_json_mappings).build()


# JSON encoder/decoder for `DataObjectReplicaCollection`
class DataObjectReplicaCollectionJSONEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._replica_encoder = DataObjectReplicaJSONEncoder(*args, **kwargs)   # type: JSONEncoder

    def default(self, data_object_replica_collection: DataObjectReplicaCollection) -> PrimitiveJsonSerializableType:
        if not isinstance(data_object_replica_collection, DataObjectReplicaCollection):
            return super().default(data_object_replica_collection)
        return [self._replica_encoder.default(replica) for replica in data_object_replica_collection]

class DataObjectReplicaCollectionJSONDecoder(JSONDecoder, ParsedJSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._replica_decoder = DataObjectReplicaJSONDecoder(*args, **kwargs)   # type: JSONDecoder

    def decode(self, json_as_string: str, **kwargs) -> DataObjectReplicaCollection:
        json_as_dict = json.loads(json_as_string)
        return self.decode_parsed(json_as_dict)

    def decode_parsed(self, json_as_dict: dict) -> DataObjectReplicaCollection:
        if not isinstance(json_as_dict, List):
            return super().decode(json_as_dict)
        return DataObjectReplicaCollection([self._replica_decoder.decode(json.dumps(item)) for item in json_as_dict])


# JSON encoder/decoder for `IrodsMetadata`
class IrodsMetadataJSONEncoder(JSONEncoder):
    def default(self, irods_metadata: IrodsMetadata) -> PrimitiveJsonSerializableType:
        if not isinstance(irods_metadata, IrodsMetadata):
            return super().default(irods_metadata)
        avus = []
        for key, values in irods_metadata.items():
            for value in values:
                avus.append({
                    BATON_AVU_ATTRIBUTE_PROPERTY: key,
                    BATON_AVU_VALUE_PROPERTY: value
                })
        return avus

class IrodsMetadataJSONDecoder(JSONDecoder, ParsedJSONDecoder):
    def decode(self, json_as_string: str, **kwargs) -> IrodsMetadata:
        json_as_dict = json.loads(json_as_string)
        return self.decode_parsed(json_as_dict)

    def decode_parsed(self, json_as_dict: dict) -> IrodsMetadata:
        if not isinstance(json_as_dict, List):
            return super().decode(json_as_dict)
        irods_metadata = IrodsMetadata()
        for item in json_as_dict:
            assert isinstance(item, dict)
            attribute = item[BATON_AVU_ATTRIBUTE_PROPERTY]
            value = item[BATON_AVU_VALUE_PROPERTY]
            irods_metadata.add(attribute, value)
        return irods_metadata


# JSON encoder/decoder for `IrodsEntity`
_irods_entity_json_mappings = [
    JsonPropertyMapping(BATON_ACL_PROPERTY, "access_controls", "access_controls",
                        encoder_cls=AccessControlSetJSONEncoder,
                        decoder_cls=AccessControlSetJSONDecoder, optional=True),
    JsonPropertyMapping(BATON_AVU_PROPERTY, "metadata", "metadata",
                        encoder_cls=IrodsMetadataJSONEncoder, decoder_cls=IrodsMetadataJSONDecoder, optional=True)
]
_IrodsEntityJSONEncoder = MappingJSONEncoderClassBuilder(IrodsEntity, _irods_entity_json_mappings).build()
_IrodsEntityJSONDecoder = MappingJSONDecoderClassBuilder(IrodsEntity, _irods_entity_json_mappings).build()


# JSON encoder/decoder for `DataObject`
_data_object_json_mappings = [
    JsonPropertyMapping(None, "path", "path",
                        json_property_getter=lambda json_as_dict: json_as_dict[BATON_COLLECTION_PROPERTY]
                                                                  + "/" + json_as_dict[BATON_DATA_OBJECT_PROPERTY]),
    JsonPropertyMapping(BATON_COLLECTION_PROPERTY,
                        object_property_getter=lambda irods_entity: irods_entity.get_collection_path()),
    JsonPropertyMapping(BATON_DATA_OBJECT_PROPERTY,
                        object_property_getter=lambda irods_entity: irods_entity.get_name()),
    JsonPropertyMapping(BATON_REPLICA_PROPERTY, "replicas", "replicas",
                        encoder_cls=DataObjectReplicaCollectionJSONEncoder,
                        decoder_cls=DataObjectReplicaCollectionJSONDecoder,
                        optional=True)
]
_DataObjectJSONEncoder = MappingJSONEncoderClassBuilder(
    DataObject, _data_object_json_mappings, (_IrodsEntityJSONEncoder, )).build()
_DataObjectJSONDecoder = MappingJSONDecoderClassBuilder(
    DataObject, _data_object_json_mappings, (_IrodsEntityJSONDecoder, )).build()

# Issue with baton https://github.com/wtsi-npg/baton/issues/146 makes dealing with timestamps a pain
class DataObjectJSONEncoder(_DataObjectJSONEncoder):
    def default(self, serializable: Union[DataObject, List[DataObject]]) -> Dict:
        if isinstance(serializable, List):
            return [self.default(data_object) for data_object in serializable]
        data_object_as_json = super().default(serializable)
        if serializable.replicas is not None:
            DataObjectJSONEncoder._serialize_timestamps(data_object_as_json, serializable)
        return data_object_as_json

    @staticmethod
    def _serialize_timestamps(data_object_as_json: Dict, data_object: DataObject):
        data_object_as_json[BATON_TIMESTAMP_PROPERTY] = []
        timestamps_as_json = data_object_as_json[BATON_TIMESTAMP_PROPERTY]
        for replica in data_object.replicas:
            if replica.created is not None:
                timestamps_as_json.append({
                    BATON_TIMESTAMP_CREATED_PROPERTY: replica.created.isoformat(),
                    BATON_TIMESTAMP_REPLICA_NUMBER_LINK_PROPERTY: replica.number
                })
            if replica.last_modified is not None:
                timestamps_as_json.append({
                    BATON_TIMESTAMP_LAST_MODIFIED_PROPERTY: replica.last_modified.isoformat(),
                    BATON_TIMESTAMP_REPLICA_NUMBER_LINK_PROPERTY: replica.number
                })

class DataObjectJSONDecoder(_DataObjectJSONDecoder):
    _DATE_PARSER = parser()

    def decode_parsed(self, json_as_dict: Union[Dict, List[Dict]]) -> DataObject:
        if isinstance(json_as_dict, List):
            return [self.decode_parsed(data_object_as_json) for data_object_as_json in json_as_dict]
        data_object = super().decode_parsed(json_as_dict)
        assert isinstance(data_object, DataObject)
        if data_object.replicas is not None and BATON_TIMESTAMP_PROPERTY in json_as_dict:
            timestamps_as_json = json_as_dict[BATON_TIMESTAMP_PROPERTY]
            DataObjectJSONDecoder._deserialize_timestamps_as_json(data_object, timestamps_as_json)
        return data_object

    @staticmethod
    def _deserialize_timestamps_as_json(data_object: DataObject, timestamps_as_json: Dict):
        for timestamp_as_json in timestamps_as_json:
            replica_number = timestamp_as_json[BATON_TIMESTAMP_REPLICA_NUMBER_LINK_PROPERTY]
            replica = data_object.replicas.get_by_number(replica_number)
            assert replica is not None
            if BATON_TIMESTAMP_CREATED_PROPERTY in timestamp_as_json:
                created_date_as_json = timestamp_as_json[BATON_TIMESTAMP_CREATED_PROPERTY]
                replica.created = DataObjectJSONDecoder._DATE_PARSER.parse(created_date_as_json)
            elif BATON_TIMESTAMP_LAST_MODIFIED_PROPERTY in timestamp_as_json:
                last_modified_date_as_json = timestamp_as_json[BATON_TIMESTAMP_LAST_MODIFIED_PROPERTY]
                replica.last_modified = DataObjectJSONDecoder._DATE_PARSER.parse(last_modified_date_as_json)


# JSON encoder/decoder for `Collection`
_collection_json_mappings = [
    JsonPropertyMapping(BATON_COLLECTION_PROPERTY, "path", "path")
]
CollectionJSONEncoder = MappingJSONEncoderClassBuilder(
    Collection, _collection_json_mappings, (_IrodsEntityJSONEncoder,)).build()
CollectionJSONDecoder = MappingJSONDecoderClassBuilder(
    Collection, _collection_json_mappings, (_IrodsEntityJSONDecoder, )).build()


# JSON encoder/decoder for `SearchCriterion`
def _parse_operator_as_string(operator_as_string: str) -> ComparisonOperator:
    for key, value in BATON_SEARCH_CRITERION_COMPARISON_OPERATORS.items():
        if value == operator_as_string:
            return key
    raise ValueError("Invalid operator: `%s`" % operator_as_string)

_search_criterion_json_mappings = [
    JsonPropertyMapping(BATON_SEARCH_CRITERION_ATTRIBUTE_PROPERTY, "attribute", "attribute"),
    JsonPropertyMapping(BATON_SEARCH_CRITERION_VALUE_PROPERTY, "value", "value"),
    JsonPropertyMapping(BATON_SEARCH_CRITERION_COMPARISON_OPERATOR_PROPERTY,
                        object_property_getter=lambda search_criterion: BATON_SEARCH_CRITERION_COMPARISON_OPERATORS[
                            search_criterion.comparison_operator],
                        object_constructor_parameter_name="comparison_operator",
                        object_constructor_argument_modifier=lambda operator_as_string: _parse_operator_as_string(
                            operator_as_string))
]
SearchCriterionJSONEncoder = MappingJSONEncoderClassBuilder(SearchCriterion, _search_criterion_json_mappings).build()
SearchCriterionJSONDecoder = MappingJSONDecoderClassBuilder(SearchCriterion, _search_criterion_json_mappings).build()


# JSON encoder/decoder for `SpecificQuery`
_specific_query_json_mappings = [
    JsonPropertyMapping(BATON_SPECIFIC_QUERY_ALIAS_PROPERTY, "alias", "alias"),
    JsonPropertyMapping(BATON_SPECIFIC_QUERY_SQL_PROPERTY, "sql", "sql")
]
SpecificQueryJSONEncoder = MappingJSONEncoderClassBuilder(SpecificQuery, _specific_query_json_mappings).build()
SpecificQueryJSONDecoder = MappingJSONDecoderClassBuilder(SpecificQuery, _specific_query_json_mappings).build()


# JSON encoder for `PreparedSpecificQuery`
_prepared_specific_query_json_mappings = [
    JsonPropertyMapping("sql", "alias", "alias"),
    JsonPropertyMapping(BATON_SPECIFIC_QUERY_ARGUMENTS_PROPERTY, "query_arguments", "query_arguments")
]
PreparedSpecificQueryJSONEncoder = MappingJSONEncoderClassBuilder(
    PreparedSpecificQuery, _prepared_specific_query_json_mappings).build()
