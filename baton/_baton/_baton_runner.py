import json
import logging
import os
import subprocess
import time
from abc import ABCMeta
from datetime import timedelta
from enum import Enum
from typing import Any, List, Dict, Optional

from baton._baton._constants import BATON_ERROR_MESSAGE_KEY, IRODS_ERROR_USER_FILE_DOES_NOT_EXIST, BATON_ERROR_PROPERTY,\
    BATON_ERROR_CODE_KEY, IRODS_ERROR_CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME, IRODS_ERROR_CAT_SUCCESS_BUT_WITH_NO_INFO, \
    IRODS_ERROR_CAT_INVALID_ARGUMENT

_logger = logging.getLogger(__name__)


class BatonBinary(Enum):
    """
    Names of baton binaries.
    """
    BATON = "baton"
    BATON_METAQUERY = "baton-metaquery"
    BATON_LIST = "baton-list"
    BATON_SPECIFIC_QUERY = "baton-specificquery"
    BATON_GET = "baton-get"
    BATON_METAMOD = "baton-metamod"
    BATON_CHMOD = "baton-chmod"


class BatonRunner(metaclass=ABCMeta):
    """
    Baton query runner.
    """
    @staticmethod
    def validate_baton_binaries_location(baton_binaries_directory: str) -> Optional[Exception]:
        """
        Validates that the given directory contains the baton binaries required to use the runner.
        :param baton_binaries_directory: the directory to check
        :return: exception that describes the issue else `None` if no issues
        """
        if os.path.isfile(baton_binaries_directory):
            return ValueError("The given baton binary directory (%s) is not a directory! Be sure to provide the path "
                              "to the directory containing the baton binaries, not the binary named `baton`")

        for baton_binary in BatonBinary:
            binary_location = os.path.join(baton_binaries_directory, baton_binary.value)
            if not (os.path.isfile(binary_location) and os.access(binary_location, os.X_OK)):
                return ValueError("The given baton binary directory (%s) did not contain all of the required binaries "
                                  "with executable permissions (%s)"
                                  % (baton_binaries_directory, [name.value for name in BatonBinary]))

        return None

    @staticmethod
    def _raise_any_errors_given_in_baton_out(baton_out_as_json: List[Dict]):
        """
        Raises any errors that baton has expressed in its output.
        :param baton_out_as_json: the output baton gave as parsed serialization
        """
        if not isinstance(baton_out_as_json, list):
            baton_out_as_json = [baton_out_as_json]

        for baton_item_as_json in baton_out_as_json:
            if BATON_ERROR_PROPERTY in baton_item_as_json:
                error = baton_item_as_json[BATON_ERROR_PROPERTY]
                error_message = error[BATON_ERROR_MESSAGE_KEY]
                error_code = error[BATON_ERROR_CODE_KEY]

                # Working around baton issue: https://github.com/wtsi-npg/baton/issues/155
                if error_code == IRODS_ERROR_USER_FILE_DOES_NOT_EXIST or \
                        (error_code == IRODS_ERROR_CAT_INVALID_ARGUMENT and "Failed to modify permissions" in error_message):
                    raise FileNotFoundError(error_message)
                elif error_code == IRODS_ERROR_CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME \
                        or error_code == IRODS_ERROR_CAT_SUCCESS_BUT_WITH_NO_INFO:
                    raise KeyError(error_message)
                else:
                    raise RuntimeError(error_message)

    def __init__(self, baton_binaries_directory: str, skip_baton_binaries_validation: bool=False,
                 timeout_queries_after: timedelta=None):
        """
        Constructor.
        :param baton_binaries_directory: the host of baton's binaries
        :param irods_query_zone: the iRODS zone to query
        :param skip_baton_binaries_validation: skips validation of baton binaries (intending for testing only)
        """
        if not skip_baton_binaries_validation:
            exception = BatonRunner.validate_baton_binaries_location(baton_binaries_directory)
            if exception is not None:
                raise exception

        self._baton_binaries_directory = baton_binaries_directory
        self.timeout_queries_after = timeout_queries_after

    def run_baton_query(self, baton_binary: BatonBinary, program_arguments: List[str]=None, input_data: Any=None) \
            -> List[Dict]:
        """
        Runs a baton query.
        :param baton_binary: the baton binary to use
        :param program_arguments: arguments to give to the baton binary
        :param input_data: input data to the baton binary
        :return: parsed serialization returned by baton
        """
        if program_arguments is None:
            program_arguments = []

        baton_binary_location = os.path.join(self._baton_binaries_directory, baton_binary.value)
        program_arguments = [baton_binary_location] + program_arguments

        _logger.info("Running baton command: '%s' with data '%s'" % (program_arguments, input_data))
        start_at = time.monotonic()
        baton_out = self._run_command(program_arguments, input_data=input_data)
        time_taken_to_run_query = time.monotonic() - start_at
        _logger.debug("baton output (took %s seconds, wall time): %s" % (time_taken_to_run_query, baton_out))

        if len(baton_out) == 0:
            return []
        if len(baton_out) > 0 and baton_out[0] != '[':
            # If information about multiple files is returned, baton does not return valid JSON - it returns a line
            # separated list of JSON, where each line corresponds to a different file
            baton_out = "[%s]" % baton_out.replace('\n', ',')

        baton_out_as_json = json.loads(baton_out)
        BatonRunner._raise_any_errors_given_in_baton_out(baton_out_as_json)

        return baton_out_as_json

    def _run_command(self, arguments: List[str], input_data: Any=None, output_encoding: str="utf-8") -> str:
        """
        Run a command as a subprocess.

        Ignores errors given over stderr if there is output on stdout (this is the case where baton has been run
        correctly and has expressed the error in it's JSON out, which can be handled more appropriately upstream to this
        method.)
        :param arguments: the arguments to run
        :param input_data: the input data to pass to the subprocess
        :param output_encoding: optional specification of the output encoding to expect
        :return: the process' standard out
        """
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        if isinstance(input_data, List):
            for to_write in input_data:
                to_write_as_json = json.dumps(to_write)
                process.stdin.write(str.encode(to_write_as_json))
            input_data = None
        else:
            input_data = str.encode(json.dumps(input_data))

        timeout_in_seconds = self.timeout_queries_after.total_seconds() if self.timeout_queries_after is not None \
            else None
        out, error = process.communicate(input=input_data, timeout=timeout_in_seconds)
        if len(out) == 0 and len(error) > 0:
            raise RuntimeError(error)

        return out.decode(output_encoding).rstrip()
