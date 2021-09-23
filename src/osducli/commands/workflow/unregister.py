# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Workflow list command"""

import click

from osducli.click_cli import State, global_params
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_WORKFLOW_URL


# click entry point
@click.command()
@click.option("-n", "--name", help="DAG Name", required=True)
@handle_cli_exceptions
@global_params
def _click_command(state: State, name: str) -> dict:
    """Un-register an Airflow workflow from OSDU"""
    return unregister_workflow(state, name)


def unregister_workflow(state: State, name: str) -> dict:
    """Un-register an Airflow workflow from OSDU

    Args:
        state (State): Global state
        name (str): DAG Name

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)
    connection.cli_delete(CONFIG_WORKFLOW_URL, "workflow/" + name, [204])
