# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entitlements my groups command"""

import click
from osdu.entitlements import EntitlementsClient

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


# click entry point
@click.command()
@click.option("-m", "--member", help="Email of the member to be added.", required=True)
@click.option("-g", "--group", help="Email address of the group", required=True)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, member: str, group: str):
    """Add members to a group."""
    return add_member(state, member, group)


def add_member(state: State, member: str, group: str) -> dict:
    """Add members to a group.

    Args:
        state (State): Global state
        member (str): Email address of the member
        group (str): Email address of the group

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)

    entitlements_client = EntitlementsClient(connection)
    json_response = entitlements_client.add_member_to_group(member, group)
    return json_response
