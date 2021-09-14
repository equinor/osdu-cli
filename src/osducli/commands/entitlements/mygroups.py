# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""version command"""

import sys

import click
from osdu.entitlements import EntitlementsClient

import osducli
from osducli.click_cli import global_params
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


# click entry point
@click.command()
@global_params
@handle_cli_exceptions
def _click_command(state):
    """Version information"""
    return list_my_groups(state)


def list_my_groups(state):

    connection = CliOsduClient()

    entitlements_client = EntitlementsClient(connection)
    json_response = entitlements_client.list_groups()
    state.jmes = "groups[name]"
    return json_response
