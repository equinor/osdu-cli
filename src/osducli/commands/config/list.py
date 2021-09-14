# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entry or launch point for CLI.

Handles creating and launching a CLI to handle a user command."""

import configparser
import os
import sys

import click
from knack.invocation import CommandInvoker
from knack.util import CommandResultItem

from osducli import config
from osducli.click_cli import global_params
from osducli.cliclient import handle_cli_exceptions
from osducli.commands.config.consts import (
    AUTHENTICATION_LIST,
    MSG_CLOSING,
    MSG_GLOBAL_SETTINGS_LOCATION,
    MSG_HEADING_CURRENT_CONFIG_INFO,
    MSG_HEADING_ENV_VARS,
    MSG_INTRO,
    MSG_PROMPT_ACL_OWNER,
    MSG_PROMPT_ACL_VIEWER,
    MSG_PROMPT_AUTHENTICATION_MODE,
    MSG_PROMPT_AUTHORITY,
    MSG_PROMPT_CLIENT_ID,
    MSG_PROMPT_CLIENT_SECRET,
    MSG_PROMPT_CONFIG,
    MSG_PROMPT_CONFIG_ENTITLEMENTS_URL,
    MSG_PROMPT_DATA_PARTITION,
    MSG_PROMPT_FILE_URL,
    MSG_PROMPT_GLOBAL_OUTPUT,
    MSG_PROMPT_LEGAL_TAG,
    MSG_PROMPT_MANAGE_GLOBAL,
    MSG_PROMPT_REFRESH_TOKEN,
    MSG_PROMPT_SCHEMA_URL,
    MSG_PROMPT_SCOPES,
    MSG_PROMPT_SEARCH_URL,
    MSG_PROMPT_SERVER,
    MSG_PROMPT_STORAGE_URL,
    MSG_PROMPT_TOKEN_ENDPOINT_URL,
    MSG_PROMPT_UNIT_URL,
    MSG_PROMPT_WORKFLOW_URL,
    OUTPUT_LIST,
)
from osducli.config import CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX, CLI_NAME
from osducli.osdu_cli import OsduCli
from osducli.osdu_command_help import OsduCommandHelp
from osducli.osdu_command_loader import OsduCommandLoader

# from osducli.util import is_help_command


@click.command()
@global_params
@handle_cli_exceptions
def _click_command(state):
    # def _click_command(ctx, debug, config, hostname):
    """List configuration"""
    list(state)


def _print_cur_configuration(cli_config: config.CLIConfig):
    from osducli.config import CLI_ENV_VAR_PREFIX

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
        print(f"Try running 'osdcli config update' or 'osdcli config set'")


def list(state):
    _print_cur_configuration(state.config)


# @_click_command.command()
# @click.pass_obj
# def set_config(command):
#     """Sensors commands"""
#     click.echo(f"set_config")


# @_click_command.command()
# @click.pass_obj
# def list_config(command):
#     """list config"""
#     click.echo(f"list_config")
