# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Code to handle status commands"""

from configparser import NoSectionError, NoOptionError
from urllib.parse import urljoin

import requests
from knack.commands import CLICommand
from knack.log import get_logger

from osducli.connection import OsduConnection

logger = get_logger(__name__)


def _get_status(server, api, path, headers):
    url = urljoin(server, api) + path
    response = requests.get(url, headers=headers)
    return response.status_code, response.reason


def status(cmd: CLICommand):   # pylint: disable=unused-argument
    """status command entry point

    Returns:
        [type]: [description]
    """
    connection = OsduConnection()

    try:
        response = connection.get('search_url', 'health/readiness_check')
        print(f"Search service         {response.status_code}\t {response.reason}")

        response = connection.get('schema_url', 'schema?limit=1')
        print(f"Schema service         {response.status_code}\t {response.reason}")

        response = connection.get('workflow_url', 'readiness_check')
        print(f"Workflow service       {response.status_code}\t {response.reason}")

        response = connection.get('storage_url', 'health')
        print(f"Storage service        {response.status_code}\t {response.reason}")

        response = connection.get('file_url', 'readiness_check')
        print(f"File service           {response.status_code}\t {response.reason}")

    except (IndexError, NoSectionError, NoOptionError) as ex:
        logger.error("'%s' missing from configuration. Run osducli configure or add manually", ex.args[0])
