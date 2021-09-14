# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entitlements groups members command"""

import click
from osdu.entitlements import EntitlementsClient

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


# click entry point
@click.command()
@click.option("-g", "--group", help="Email address of the group", required=True)
@handle_cli_exceptions
@command_with_output("members[*]")
def _click_command(state: State, group: str):
    """List members in a group."""
    return list_group_members(state, group)


def list_group_members(state: State, group: str) -> dict:
    """Delete members from a group

    Args:
        state (State): Global state
        group (str): Email address of the group

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)

    entitlements_client = EntitlementsClient(connection)
    json_response = entitlements_client.list_group_members(group)
    return json_response
