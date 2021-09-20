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
@handle_cli_exceptions
@command_with_output("groups[*]")
def _click_command(state: State):
    """List groups you have access to."""
    return list_my_groups(state)


def list_my_groups(state: State) -> dict:
    """Get the calling users groups

    Args:
        state (State): Global state

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)

    entitlements_client = EntitlementsClient(connection)
    json_response = entitlements_client.list_groups()
    return json_response
