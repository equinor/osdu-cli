# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Constants for configure commands"""

OUTPUT_LIST = [
    {'name': 'json', 'desc': 'JSON formatted output that most closely matches API responses.'},
    {'name': 'jsonc', 'desc': 'Colored JSON formatted output that most closely matches API responses.'},
    {'name': 'table', 'desc': 'Human-readable output format.'},
    {'name': 'tsv', 'desc': 'Tab- and Newline-delimited. Great for GREP, AWK, etc.'},
    {'name': 'yaml', 'desc': 'YAML formatted output. An alternative to JSON. Great for configuration files.'},
    {'name': 'yamlc', 'desc': 'Colored YAML formatted output. An alternative to JSON. Great for configuration files.'},
    {'name': 'none', 'desc': 'No output, except for errors and warnings.'}
]

MSG_INTRO = '\nWelcome to the OSDU CLI! This command will guide you through logging in and ' \
            'setting some default values.\n'
MSG_CLOSING = '\nYou\'re all set! Here are some commands to try:\n' \
              ' $ osducli login\n' \
              ' $ osducli list\n'

MSG_GLOBAL_SETTINGS_LOCATION = 'Your settings can be found at {}'

MSG_HEADING_CURRENT_CONFIG_INFO = 'Your current configuration is as follows:'
MSG_HEADING_ENV_VARS = '\nEnvironment variables:'

MSG_PROMPT_MANAGE_GLOBAL = '\nDo you wish to change your settings?'
MSG_PROMPT_GLOBAL_OUTPUT = '\nWhat default output format would you like?'
MSG_PROMPT_SERVER = '\nWhat is the OSDU API Server? '
MSG_PROMPT_SEARCH_URL = '\nWhat is the OSDU Search API url? '
MSG_PROMPT_TOKEN_ENDPOINT_URL = '\nWhat is the Authentication Token endpoint url? '
MSG_PROMPT_DATA_PARTITION = '\nWhat is the data partition name? '
MSG_PROMPT_REFRESH_TOKEN = '\nWhat is the refresh token? '
MSG_PROMPT_CLIENT_ID = '\nWhat is the client id? '
MSG_PROMPT_CLIENT_SECRET = '\nWhat is the client secret? '
