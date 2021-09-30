# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entitlements groups delete command"""

import click
from osdu.entitlements import EntitlementsClient

from osducli.click_cli import State, global_params
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


# click entry point
@click.command()
@click.option("-g", "--group", help="Email address of the group", required=True)
@handle_cli_exceptions
@global_params
def _click_command(state: State, group: str):
    """Delete a group."""
    delete_group(state, group)


def delete_group(state: State, group: str):
    """Delete a group

    Args:
        state (State): Global state
        group (str): Unique email identifier of the group
    """
    connection = CliOsduClient(state.config)

    entitlements_client = EntitlementsClient(connection)
    entitlements_client.delete_group(group)
