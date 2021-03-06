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
@click.option("-k", "--kind", "kind", help="kind to search for")
@click.option("-id", "--id", "_id", help="id to search for")
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, kind: str, _id: str):
    """Query search service"""
    return query(state, kind, _id)


def query(state: State, kind: str, id: str):  # pylint: disable=invalid-name,redefined-builtin
    """Query search service

    Args:
        state (State): Global state
    """
    connection = CliOsduClient(state.config)

    search_client = SearchClient(connection)
    json_response = search_client.query(kind, id)

    return json_response
