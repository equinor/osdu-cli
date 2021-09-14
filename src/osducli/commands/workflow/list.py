# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Workflow list command"""

import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_WORKFLOW_URL


# click entry point
@click.command()
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State) -> dict:
    """List available workflows"""
    return list_workflows(state)


def list_workflows(state: State) -> dict:
    """List available workflows

    Args:
        state (State): Global state

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)
    response_json = connection.cli_get_returning_json(CONFIG_WORKFLOW_URL, "workflow?prefix=")
    return response_json
