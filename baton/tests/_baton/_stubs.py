from baton._baton._baton_runner import BatonRunner
from baton._baton.baton_custom_object_mappers import BatonCustomObjectMapper


class StubBatonRunner(BatonRunner):
    """
    Stub `BatonRunner`.
    """


class StubBatonCustomObjectMapper(BatonCustomObjectMapper[dict]):
    """
    Stub `BatonCustomObjectMapper`.
    """
    def _object_deserialiser(self, object_as_json: dict) -> dict:
        return object_as_json
