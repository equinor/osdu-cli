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
@click.option("-n", "--name", help="DAG Name", required=True)
@click.option("-d", "--description", help="Description", required=True)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, name: str, description: str) -> dict:
    """Register an Airflow workflow with OSDU"""
    return register_workflow(state, name, description)


def register_workflow(state: State, name: str, description: str) -> dict:
    """Register an Airflow workflow with OSDU

    Args:
        state (State): Global state
        name (str): DAG Name
        description (str): Description

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)

    request = {
        "description": description,
        "registrationInstructions": {},
        "workflowName": name,
    }
    response_json = connection.cli_post_returning_json(CONFIG_WORKFLOW_URL, "workflow", request)
    return response_json
