# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Config listupdate command"""


import os

import click

from osducli.click_cli import global_params
from osducli.cliclient import handle_cli_exceptions
from osducli.commands.config.consts import (
    MSG_HEADING_CURRENT_CONFIG_INFO,
    MSG_HEADING_ENV_VARS,
)
from osducli.config import CLI_ENV_VAR_PREFIX, CLIConfig

# from osducli.util import is_help_command


@click.command()
@global_params
@handle_cli_exceptions
def _click_command(state):
    # def _click_command(ctx, debug, config, hostname):
    """List configuration"""
    config_list(state)


def print_cur_configuration(cli_config: CLIConfig):
    """Print the current configuration

    Args:
        cli_config (CLIConfig): CLIConfig
    """

    print("TODO: accesses config_parser file directly - might show actual used values instead")
    print(MSG_HEADING_CURRENT_CONFIG_INFO)
    if cli_config.config_parser:
        for section in cli_config.config_parser.sections():
            print()
            print("[{}]".format(section))
            for name, value in cli_config.config_parser.items(section):
                print("{} = {}".format(name, value))
        env_vars = [ev for ev in os.environ if ev.startswith(CLI_ENV_VAR_PREFIX)]
        if env_vars:
            print(MSG_HEADING_ENV_VARS)
            print("\n".join(["{} = {}".format(ev, os.environ[ev]) for ev in env_vars]))
    else:
        print(f"No config file found at {cli_config.config_path}. run osdcli ")
        print("Try running 'osdcli config update' or 'osdcli config set'")


def config_list(state):
    """List configuration

    Args:
        state (State): Global state
    """
    print_cur_configuration(state.config)
