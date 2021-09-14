# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""

from osdu.search import SearchClient

from osducli.cliclient import CliOsduClient, handle_cli_exceptions


def version():
    """Search service"""
    print("NOT IMPLEMENTED - DUMMY CODE / NOT VALID CALL")


@handle_cli_exceptions
def query(id: str):  #  TO FIX later pylint: disable=invalid-name,redefined-builtin
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    connection = CliOsduClient()

    search_client = SearchClient(connection)
    json_response = search_client.query_by_id(id)

    return json_response
