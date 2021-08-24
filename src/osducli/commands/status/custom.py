# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Code to handle status commands"""

from configparser import NoSectionError, NoOptionError

from knack.commands import CLICommand
from knack.log import get_logger

from osducli.config import (CONFIG_FILE_URL,
                            CONFIG_SCHEMA_URL,
                            CONFIG_SEARCH_URL,
                            CONFIG_STORAGE_URL,
                            CONFIG_UNIT_URL,
                            CONFIG_WORKFLOW_URL)
from osducli.cliclient import CliOsduClient

logger = get_logger(__name__)


def status(cmd: CLICommand):   # pylint: disable=unused-argument
    """status command entry point

    Returns:
        [type]: [description]
    """
    connection = CliOsduClient()

    try:
        response = connection.cli_get(CONFIG_FILE_URL, 'readiness_check')
        print(f"File service           {response.status_code}\t {response.reason}")

        response = connection.cli_get(CONFIG_SCHEMA_URL, 'schema?limit=1')
        print(f"Schema service         {response.status_code}\t {response.reason}")

        response = connection.cli_get(CONFIG_SEARCH_URL, 'health/readiness_check')
        print(f"Search service         {response.status_code}\t {response.reason}")

        response = connection.cli_get(CONFIG_STORAGE_URL, 'health')
        print(f"Storage service        {response.status_code}\t {response.reason}")

        response = connection.cli_get(CONFIG_UNIT_URL, '../_ah/readiness_check')
        print(f"Unit service           {response.status_code}\t {response.reason}")

        response = connection.cli_get(CONFIG_WORKFLOW_URL, '../readiness_check')
        print(f"Workflow service       {response.status_code}\t {response.reason}")

    except (IndexError, NoSectionError, NoOptionError) as ex:
        logger.error("'%s' missing from configuration. Run osducli configure or add manually", ex.args[0])
