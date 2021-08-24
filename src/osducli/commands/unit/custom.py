# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""

from osducli.cliclient import CliOsduClient
from osducli.config import CONFIG_UNIT_URL


def unit_list():
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    connection = CliOsduClient()
    json = connection.cli_get_returning_json(CONFIG_UNIT_URL, 'unit?limit=10000')
    return json
