from baton._baton.baton_custom_object_mappers import BatonSpecificQueryMapper
from baton._baton.baton_entity_mappers import BatonDataObjectMapper, BatonCollectionMapper


class Connection:
    """
    Pseudo connection to iRODS.
    """
    def __init__(self, baton_binaries_directory: str, skip_baton_binaries_validation: bool=False):
        """
        Constructor.
        :param baton_binaries_directory: the directory host of the baton binaries
        :param skip_baton_binaries_validation: whether checks on if the correct baton binaries exist within the given
        directory should be skipped
        """
        self.data_object = BatonDataObjectMapper(baton_binaries_directory, skip_baton_binaries_validation)
        self.collection = BatonCollectionMapper(baton_binaries_directory, skip_baton_binaries_validation)
        self.specific_query = BatonSpecificQueryMapper(baton_binaries_directory, skip_baton_binaries_validation)


def connect_to_irods_with_baton(baton_binaries_directory: str, skip_baton_binaries_validation: bool=False) \
        -> Connection:
    """
    Convenience method to create a pseudo connection to iRODS.
    :param baton_binaries_directory: see `Connection.__init__`
    :param skip_baton_binaries_validation: see `Connection.__init__`
    :return: pseudo connection to iRODS
    """
    return Connection(baton_binaries_directory, skip_baton_binaries_validation)
