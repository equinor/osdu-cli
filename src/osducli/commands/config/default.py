# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""config default command"""

import click

from osducli.click_cli import State, global_params
from osducli.cliclient import handle_cli_exceptions
from osducli.state import get_default_config_path, set_default_config_path
from osducli.util.prompt import prompt


# click entry point
@click.command()
@handle_cli_exceptions
@global_params
def _click_command(state: State):
    """Set the default config file"""
    config_default(state)


def config_default(state: State):
    """Set the default config file

    Args:
        state (State): Global state
    """
    config_file = get_default_config_path()
    default_config_file = get_default_config_path(locate=True)
    if config_file:
        print(f"Currently using '{config_file}'")
    elif default_config_file:
        print(f"Currently using default config '{default_config_file}'")

    if state.config_path is None:
        config_file = prompt("What config file should be the default:")
    else:
        config_file = state.config_path
    if config_file:
        print("TODO CHeck Path")
        set_default_config_path(config_file)
    else:
        print("No changes made!")
