# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Schema service list command"""

import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_SCHEMA_URL


# click entry point
@click.command()
@click.option("-k", "--kind", required=True, help="Kind of the schema")
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, kind: str):
    """Get schema"""
    return schema_get(state, kind)


def schema_get(state: State, kind: str):
    """Get schema

    Args:
        state (State): Global state
        kind (str): Kind of the schema
    """
    connection = CliOsduClient(state.config)
    url = "schema/" + kind
    json = connection.cli_get_returning_json(CONFIG_SCHEMA_URL, url)
    return json
