# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entitlements my groups command"""

import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import handle_cli_exceptions

from ..groups.members import list_group_members


# click entry point
@click.command()
@click.option("-g", "--group", help="Email address of the group", required=True)
@handle_cli_exceptions
@command_with_output("members[*]")
def _click_command(state: State, group: str):
    """List members in a group."""
    return list_group_members(state, group)
