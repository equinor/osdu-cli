# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Code to handle status commands"""

from configparser import NoOptionError, NoSectionError

from knack.commands import CLICommand
from knack.log import get_logger
from requests.models import HTTPError

from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import (CONFIG_FILE_URL, CONFIG_SCHEMA_URL,
                            CONFIG_SEARCH_URL, CONFIG_STORAGE_URL,
                            CONFIG_UNIT_URL, CONFIG_WORKFLOW_URL)

logger = get_logger(__name__)


@handle_cli_exceptions
def status(cmd: CLICommand):   # pylint: disable=unused-argument
    """status command entry point

    Returns:
        [type]: [description]
    """
    connection = CliOsduClient()

    check_print_status(connection, "File service", CONFIG_FILE_URL, 'readiness_check')
    check_print_status(connection, "Schema service", CONFIG_SCHEMA_URL, 'schema?limit=1')
    check_print_status(connection, "Search service", CONFIG_SEARCH_URL, 'health/readiness_check')
    check_print_status(connection, "Storage service", CONFIG_STORAGE_URL, 'health')
    check_print_status(connection, "Unit service", CONFIG_UNIT_URL, '../_ah/readiness_check')
    check_print_status(connection, "Workflow service", CONFIG_WORKFLOW_URL, '../readiness_check')


def check_print_status(connection: CliOsduClient, name:str, config_url_key: str, url_extra_path: str):
    """Check the status of the given service and print information"""
    try:
        response = connection.cli_get(config_url_key, url_extra_path)
        print(f"{name.ljust(20)} {response.status_code}\t {response.reason}")
    except (HTTPError) as ex:
        print(f"{name.ljust(20)} {ex.response.status_code}\t {ex.response.reason}")
