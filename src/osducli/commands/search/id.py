# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Search service query command"""

import click
from osdu.search import SearchClient

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


# click entry point
@click.command()
@click.argument("id")
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, id: str):  # noqa:W1 pylint: disable=invalid-name,redefined-builtin
    """Search for the specified id"""
    return query(state, id)


def query(state: State, id: str):  # TO FIX later pylint: disable=invalid-name,redefined-builtin
    """Search for the specified id

    Args:
        state (State): Global state
    """
    connection = CliOsduClient(state.config)

    search_client = SearchClient(connection)
    json_response = search_client.query_by_id(id)

    return json_response
