# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""
import configparser
import os
from knack.prompting import prompt, prompt_y_n, prompt_choice_list, prompt_pass
from osducli.config import get_default_from_config
from osducli.commands.configure.consts import (MSG_INTRO,
                                               MSG_CLOSING,
                                               MSG_GLOBAL_SETTINGS_LOCATION,
                                               MSG_HEADING_CURRENT_CONFIG_INFO,
                                               MSG_HEADING_ENV_VARS,
                                               MSG_PROMPT_MANAGE_GLOBAL,
                                               MSG_PROMPT_GLOBAL_OUTPUT,
                                               OUTPUT_LIST,
                                               MSG_PROMPT_SERVER,
                                               MSG_PROMPT_SEARCH_URL,
                                               MSG_PROMPT_TOKEN_ENDPOINT_URL,
                                               MSG_PROMPT_DATA_PARTITION,
                                               MSG_PROMPT_REFRESH_TOKEN,
                                               MSG_PROMPT_CLIENT_ID,
                                               MSG_PROMPT_CLIENT_SECRET)

answers = {}


def _print_cur_configuration(file_config):
    from osducli.config import SF_CLI_ENV_VAR_PREFIX
    print(MSG_HEADING_CURRENT_CONFIG_INFO)
    for section in file_config.sections():
        print()
        print('[{}]'.format(section))
        for option in file_config.options(section):
            print('{} = {}'.format(option, file_config.get(section, option)))
    env_vars = [ev for ev in os.environ if ev.startswith(SF_CLI_ENV_VAR_PREFIX)]
    if env_vars:
        print(MSG_HEADING_ENV_VARS)
        print('\n'.join(['{} = {}'.format(ev, os.environ[ev]) for ev in env_vars]))


def _handle_configuration(config):
    # print location of global configuration
    print(MSG_GLOBAL_SETTINGS_LOCATION.format(config.config_path))
    # set up the config parsers
    file_config = configparser.ConfigParser()
    config_exists = file_config.read([config.config_path])
    should_modify_global_config = False
    if config_exists:
        # print current config and prompt to allow global config modification
        _print_cur_configuration(file_config)
        should_modify_global_config = prompt_y_n(MSG_PROMPT_MANAGE_GLOBAL, default='n')
    if not config_exists or should_modify_global_config:
        output_index = prompt_choice_list(MSG_PROMPT_GLOBAL_OUTPUT, OUTPUT_LIST,
                                          default=get_default_from_config(config,
                                                                          'core',
                                                                          'output',
                                                                          OUTPUT_LIST,
                                                                          fallback=3))
        answers['output_type_prompt'] = output_index
        answers['output_type_options'] = str(OUTPUT_LIST)
        server = prompt(MSG_PROMPT_SERVER)
        search_url = prompt(MSG_PROMPT_SEARCH_URL)
        token_endpoint = prompt(MSG_PROMPT_TOKEN_ENDPOINT_URL)
        data_partition_id = prompt(MSG_PROMPT_DATA_PARTITION)
        refresh_token = prompt_pass(MSG_PROMPT_REFRESH_TOKEN)
        client_id = prompt(MSG_PROMPT_CLIENT_ID)
        client_secret = prompt_pass(MSG_PROMPT_CLIENT_SECRET)

        # save the global config
        # config.set_value('core', 'output', OUTPUT_LIST[output_index]['name'])
        # config.set_value('core', 'collect_telemetry', 'yes' if allow_telemetry else 'no')
        config.set_value('core', 'output', OUTPUT_LIST[output_index]['name'])
        if server != '':
            config.set_value('core', 'server', server)
        if search_url != '':
            config.set_value('core', 'search_url', search_url)
        if token_endpoint != '':
            config.set_value('core', 'token_endpoint', token_endpoint)
        if data_partition_id != '':
            config.set_value('core', 'data-partition-id', data_partition_id)
        if refresh_token != '':
            config.set_value('core', 'token_type', 'access_token')
            config.set_value('core', 'refresh_token', refresh_token)
        if client_id != '':
            config.set_value('core', 'client_id', client_id)
        if client_secret != '':
            config.set_value('core', 'client_secret', client_secret)


def configure(cmd):
    """[summary]

    Args:
        cmd ([type]): [description]
    """
    print(MSG_INTRO)
    _handle_configuration(cmd.cli_ctx.config)
    print(MSG_CLOSING)
