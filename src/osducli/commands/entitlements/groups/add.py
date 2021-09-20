# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entitlements groups add command"""

import click
from osdu.entitlements import EntitlementsClient

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


# click entry point
@click.command()
@click.option("-g", "--group", help="Email address of the group", required=True)
@handle_cli_exceptions
@command_with_output("")
def _click_command(state: State, group: str):
    """Add a group."""
    return add_group(state, group)


def add_group(state: State, group: str) -> dict:
    """Add a group

    Args:
        state (State): Global state
        group (str): Email address of the group

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)

    entitlements_client = EntitlementsClient(connection)
    json_response = entitlements_client.add_group(group)
    return json_response
