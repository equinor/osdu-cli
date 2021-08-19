# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""

from osducli.connection import CliOsduConnection


def unit_list():
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    connection = CliOsduConnection()
    json = connection.cli_get_as_json('unit_url', 'unit?limit=10000')
    return json