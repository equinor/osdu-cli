# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Config update command"""

import configparser

import click

from osducli.click_cli import State, global_params
from osducli.cliclient import handle_cli_exceptions
from osducli.commands.config.consts import (
    AUTHENTICATION_LIST,
    MSG_CLOSING,
    MSG_GLOBAL_SETTINGS_LOCATION,
    MSG_INTRO,
    MSG_PROMPT_ACL_OWNER,
    MSG_PROMPT_ACL_VIEWER,
    MSG_PROMPT_AUTHENTICATION_MODE,
    MSG_PROMPT_AUTHORITY,
    MSG_PROMPT_CLIENT_ID,
    MSG_PROMPT_CLIENT_SECRET,
    MSG_PROMPT_CONFIG_ENTITLEMENTS_URL,
    MSG_PROMPT_DATA_PARTITION,
    MSG_PROMPT_FILE_URL,
    MSG_PROMPT_LEGAL_TAG,
    MSG_PROMPT_LEGAL_URL,
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
)
from osducli.commands.config.list import print_cur_configuration
from osducli.config import (
    CONFIG_ACL_OWNER,
    CONFIG_ACL_VIEWER,
    CONFIG_AUTHENTICATION_AUTHORITY,
    CONFIG_AUTHENTICATION_MODE,
    CONFIG_AUTHENTICATION_SCOPES,
    CONFIG_CLIENT_ID,
    CONFIG_CLIENT_SECRET,
    CONFIG_DATA_PARTITION_ID,
    CONFIG_ENTITLEMENTS_URL,
    CONFIG_FILE_URL,
    CONFIG_LEGAL_TAG,
    CONFIG_LEGAL_URL,
    CONFIG_REFRESH_TOKEN,
    CONFIG_SCHEMA_URL,
    CONFIG_SEARCH_URL,
    CONFIG_SERVER,
    CONFIG_STORAGE_URL,
    CONFIG_TOKEN_ENDPOINT,
    CONFIG_UNIT_URL,
    CONFIG_WORKFLOW_URL,
    CLIConfig,
    get_default_choice_index_from_config,
    get_default_from_config,
)
from osducli.util.prompt import prompt, prompt_choice_list, prompt_y_n

# from osducli.util import is_help_command


@click.command()
@click.option("-k", "--key", help="A specific key to update.")
@click.option("-v", "--value", help="Value to update key with.")
@global_params
@handle_cli_exceptions
def _click_command(state: State, key: str = None, value: str = None):
    # def _click_command(ctx, debug, config, hostname):
    """Update configuration values. This command is interactive."""
    config_update(state, key, value)


def config_update(state: State, key: str, value: str):
    """Update configuration values.

    Args:
        state (State): Global state
        group (str): Email address of the group

    Returns:
        dict: Response from service
    """
    if key is None:
        print(MSG_INTRO)
        _handle_configuration(state.config)
        print(MSG_CLOSING)
    else:
        print(f"Updating '{key}' only")
        if value is None:
            value = prompt("Enter the new value: ")
        if value != "":
            state.config.set_value("core", key, value)
        print("Done")


def _prompt_default_from_config(
    msg: str,
    config: configparser.ConfigParser,
    option: str,
    default_value_display_length: int = None,
    fallback: str = None,
):
    if config.has_option("core", option):
        default = get_default_from_config(config, "core", option)
    else:
        default = fallback

    return prompt(msg, default, default_value_display_length=default_value_display_length)


def _handle_configuration(config: CLIConfig):
    # print location of global configuration
    print(MSG_GLOBAL_SETTINGS_LOCATION.format(config.config_path))
    # set up the config parsers
    file_config = configparser.ConfigParser()
    config_exists = file_config.read([config.config_path])
    should_modify_global_config = False
    if config_exists:
        # print current config and prompt to allow global config modification
        print_cur_configuration(config)
        should_modify_global_config = prompt_y_n(MSG_PROMPT_MANAGE_GLOBAL, default="n")
    if not config_exists or should_modify_global_config:
        _configure_connection(config)

        _configure_authentication(config)


def _configure_authentication(config):
    # Setup authentication
    authentication_index = prompt_choice_list(
        MSG_PROMPT_AUTHENTICATION_MODE,
        AUTHENTICATION_LIST,
        default=get_default_choice_index_from_config(
            config, "core", CONFIG_AUTHENTICATION_MODE, AUTHENTICATION_LIST, fallback=1
        ),
    )
    config.set_value(
        "core", CONFIG_AUTHENTICATION_MODE, AUTHENTICATION_LIST[authentication_index]["name"]
    )

    # refresh_token
    if authentication_index == 0:
        token_endpoint = _prompt_default_from_config(
            MSG_PROMPT_TOKEN_ENDPOINT_URL, config, CONFIG_TOKEN_ENDPOINT, 40
        )
        refresh_token = _prompt_default_from_config(
            MSG_PROMPT_REFRESH_TOKEN, config, CONFIG_REFRESH_TOKEN, 40
        )
        client_id = _prompt_default_from_config(MSG_PROMPT_CLIENT_ID, config, CONFIG_CLIENT_ID, 40)
        client_secret = _prompt_default_from_config(
            MSG_PROMPT_CLIENT_SECRET, config, CONFIG_CLIENT_SECRET, 40
        )

        if token_endpoint != "":
            config.set_value("core", CONFIG_TOKEN_ENDPOINT, token_endpoint)
        if refresh_token != "":
            config.set_value("core", CONFIG_REFRESH_TOKEN, refresh_token)
        if client_id != "":
            config.set_value("core", CONFIG_CLIENT_ID, client_id)
        if client_secret != "":
            config.set_value("core", CONFIG_CLIENT_SECRET, client_secret)

    # msal interactive
    elif authentication_index == 1:
        authority = _prompt_default_from_config(
            MSG_PROMPT_AUTHORITY, config, CONFIG_AUTHENTICATION_AUTHORITY, 40
        )
        scopes = _prompt_default_from_config(
            MSG_PROMPT_SCOPES, config, CONFIG_AUTHENTICATION_SCOPES, 40
        )
        client_id = _prompt_default_from_config(MSG_PROMPT_CLIENT_ID, config, CONFIG_CLIENT_ID, 40)

        if authority != "":
            config.set_value("core", CONFIG_AUTHENTICATION_AUTHORITY, authority)
        if scopes != "":
            config.set_value("core", CONFIG_AUTHENTICATION_SCOPES, scopes)
        if client_id != "":
            config.set_value("core", CONFIG_CLIENT_ID, client_id)


def _configure_connection(config):  # noqa C901 pylint: disable=R0912
    server = _prompt_default_from_config(MSG_PROMPT_SERVER, config, CONFIG_SERVER)

    entitlements_url = _prompt_default_from_config(
        MSG_PROMPT_CONFIG_ENTITLEMENTS_URL,
        config,
        CONFIG_ENTITLEMENTS_URL,
        fallback="/api/entitlements/v2/",
    )
    file_url = _prompt_default_from_config(
        MSG_PROMPT_FILE_URL, config, CONFIG_FILE_URL, fallback="/api/file/v2/"
    )
    schema_url = _prompt_default_from_config(
        MSG_PROMPT_SCHEMA_URL, config, CONFIG_SCHEMA_URL, fallback="/api/schema-service/v1/"
    )
    legal_url = _prompt_default_from_config(
        MSG_PROMPT_LEGAL_URL, config, CONFIG_LEGAL_URL, fallback="/api/legal/v1/"
    )
    search_url = _prompt_default_from_config(
        MSG_PROMPT_SEARCH_URL, config, CONFIG_SEARCH_URL, fallback="/api/search/v2/"
    )
    storage_url = _prompt_default_from_config(
        MSG_PROMPT_STORAGE_URL, config, CONFIG_STORAGE_URL, fallback="/api/storage/v2/"
    )
    unit_url = _prompt_default_from_config(
        MSG_PROMPT_UNIT_URL, config, CONFIG_UNIT_URL, fallback="/api/unit/v3/"
    )
    workflow_url = _prompt_default_from_config(
        MSG_PROMPT_WORKFLOW_URL, config, CONFIG_WORKFLOW_URL, fallback="/api/workflow/v1/"
    )

    data_partition_id = _prompt_default_from_config(
        MSG_PROMPT_DATA_PARTITION, config, CONFIG_DATA_PARTITION_ID, fallback="opendes"
    )
    legal_tag = _prompt_default_from_config(
        MSG_PROMPT_LEGAL_TAG,
        config,
        CONFIG_LEGAL_TAG,
        fallback="opendes-public-usa-dataset-7643990",
    )
    acl_viewer = _prompt_default_from_config(
        MSG_PROMPT_ACL_VIEWER,
        config,
        CONFIG_ACL_VIEWER,
        fallback="data.default.viewers@opendes.contoso.com",
    )
    acl_owner = _prompt_default_from_config(
        MSG_PROMPT_ACL_OWNER,
        config,
        CONFIG_ACL_OWNER,
        fallback="data.default.owners@opendes.contoso.com",
    )

    # save the global config
    if server != "":
        config.set_value("core", CONFIG_SERVER, server)
    if entitlements_url != "":
        config.set_value("core", CONFIG_ENTITLEMENTS_URL, entitlements_url)
    if file_url != "":
        config.set_value("core", CONFIG_FILE_URL, file_url)
    if legal_url != "":
        config.set_value("core", CONFIG_LEGAL_URL, legal_url)
    if schema_url != "":
        config.set_value("core", CONFIG_SCHEMA_URL, schema_url)
    if search_url != "":
        config.set_value("core", CONFIG_SEARCH_URL, search_url)
    if storage_url != "":
        config.set_value("core", CONFIG_STORAGE_URL, storage_url)
    if unit_url != "":
        config.set_value("core", CONFIG_UNIT_URL, unit_url)
    if workflow_url != "":
        config.set_value("core", CONFIG_WORKFLOW_URL, workflow_url)

    if data_partition_id != "":
        config.set_value("core", CONFIG_DATA_PARTITION_ID, data_partition_id)
    if legal_tag != "":
        config.set_value("core", CONFIG_LEGAL_TAG, legal_tag)
    if acl_viewer != "":
        config.set_value("core", CONFIG_ACL_VIEWER, acl_viewer)
    if acl_owner != "":
        config.set_value("core", CONFIG_ACL_OWNER, acl_owner)
