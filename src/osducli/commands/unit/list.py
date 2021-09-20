# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Unit service list command"""

import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_UNIT_URL


# click entry point
@click.command()
@handle_cli_exceptions
@command_with_output("units[].[displaySymbol,name,source]")
def _click_command(state: State):
    """List unit configuration"""
    return unit_list(state)


def unit_list(state: State):
    """List unit configuration

    Args:
        state (State): Global state
    """
    connection = CliOsduClient(state.config)
    json = connection.cli_get_returning_json(CONFIG_UNIT_URL, "unit?limit=10000")
    return json
