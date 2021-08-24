# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Read and modify configuration settings related to the CLI"""

import os
import configparser
from knack.config import CLIConfig, _UNSET

# Default names
CLI_NAME = 'osducli'
CLI_CONFIG_DIR = os.path.expanduser(os.path.join('~', '.{0}'.format(CLI_NAME)))
CLI_ENV_VAR_PREFIX = CLI_NAME

CONFIG_SERVER = 'server'
CONFIG_FILE_URL = 'file_url'
CONFIG_SCHEMA_URL = 'schema_url'
CONFIG_SEARCH_URL = 'search_url'
CONFIG_STORAGE_URL = 'storage_url'
CONFIG_UNIT_URL = 'unit_url'
CONFIG_WORKFLOW_URL = 'workflow_url'

CONFIG_DATA_PARTITION_ID = 'data_partition_id'
CONFIG_LEGAL_TAG = 'legal_tag'
CONFIG_ACL_VIEWER = 'acl_viewer'
CONFIG_ACL_OWNER = 'acl_owner'

CONFIG_AUTHENTICATION_MODE = 'authentication_mode'

CONFIG_AUTHENTICATION_AUTHORITY = 'authority'
CONFIG_AUTHENTICATION_SCOPES = 'scopes'

CONFIG_TOKEN_ENDPOINT = 'token_endpoint'
CONFIG_REFRESH_TOKEN = 'refresh_token'
CONFIG_CLIENT_ID = 'client_id'
CONFIG_CLIENT_SECRET = 'client_secret'


def get_config_value(name, section=CLI_NAME, fallback=_UNSET):
    """Gets a config by name.

    In the case where the config name is not found, will use fallback value."""

    cli_config = CLIConfig(CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX)

    return cli_config.get(section, name, fallback)


def get_config_bool(name, section=CLI_NAME, fallback=_UNSET):
    """Checks if a config value is set to a valid bool value."""

    cli_config = CLIConfig(CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX)
    return cli_config.getboolean(section, name, fallback)


def get_config_int(name, section=CLI_NAME, fallback=_UNSET):
    """Checks if a config value is set to a valid int value."""

    cli_config = CLIConfig(CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX)
    return cli_config.getint(section, name, fallback)


def set_config_value(name, value, section=CLI_NAME):
    """Set a config by name to a value."""

    cli_config = CLIConfig(CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX)
    cli_config.set_value(section, name, value)


def get_default_from_config(config, section, option, fallback=1):
    """Get the default value from configuration, replacing with fallback if not found"""
    try:
        return config.get(section, option)
    except (IndexError, configparser.NoSectionError, configparser.NoOptionError):
        return fallback


def get_default_choice_index_from_config(config, section, option, choice_list, fallback=1):
    """Get index + 1 of the current choice value from cong, replacing with fallback if not found"""
    try:
        config_val = config.get(section, option)
        return [i for i, x in enumerate(choice_list)
                if 'name' in x and x['name'] == config_val][0] + 1
    except (IndexError, configparser.NoSectionError, configparser.NoOptionError):
        return fallback


def client_endpoint():
    """Cluster HTTP gateway endpoint address and port, represented as a URL."""

    return get_config_value('endpoint', None)
