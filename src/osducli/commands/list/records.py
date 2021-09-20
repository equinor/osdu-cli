# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""
import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_SEARCH_URL


@click.command()
@handle_cli_exceptions
@command_with_output("sort_by(aggregations,&key)[*].{Key:key,Count:count}")
def _click_command(state: State):
    """List count of populated records"""

    return records(state)


def records(state: State):
    """[summary]

    Args:
        state (State): Global state
    """
    request_data = {"kind": "*:*:*:*", "limit": 1, "query": "*", "aggregateBy": "kind"}

    connection = CliOsduClient(state.config)
    json_response = connection.cli_post_returning_json(CONFIG_SEARCH_URL, "query", request_data)

    return json_response
