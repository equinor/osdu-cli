# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entitlements my groups command"""

import click
from osdu.entitlements import EntitlementsClient

from osducli.click_cli import State, global_params
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


# click entry point
@click.command()
@click.option("-m", "--member", help="Email of the member to be remove.", required=True)
@click.option("-g", "--group", help="Email address of the group", required=True)
@handle_cli_exceptions
@global_params
def _click_command(state: State, member: str, group: str):
    """Remove member from a group."""
    return add_member(state, member, group)


def add_member(state: State, member: str, group: str) -> dict:
    """ "Remove member from a group.

    Args:
        state (State): Global state
        member (str): Email address of the member
        group (str): Email address of the group

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)

    entitlements_client = EntitlementsClient(connection)
    entitlements_client.remove_member_from_group(member, group)
