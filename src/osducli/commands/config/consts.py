# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Constants for config commands"""

OUTPUT_LIST = [
    {'name': 'json', 'desc': 'JSON formatted output that most closely matches API responses.'},
    {'name': 'jsonc', 'desc': 'Colored JSON formatted output that most closely matches API responses.'},
    {'name': 'table', 'desc': 'Human-readable output format.'},
    {'name': 'tsv', 'desc': 'Tab- and Newline-delimited. Great for GREP, AWK, etc.'},
    {'name': 'yaml', 'desc': 'YAML formatted output. An alternative to JSON. Great for configuration files.'},
    {'name': 'yamlc', 'desc': 'Colored YAML formatted output. An alternative to JSON. Great for configuration files.'},
    {'name': 'none', 'desc': 'No output, except for errors and warnings.'}
]

AUTHENTICATION_LIST = [
    {'name': 'refresh_token', 'desc': 'Provide a refresh token that is used to get an access token'},
    {'name': 'msal_interactive', 'desc': 'Azure interactive authentication.'}
]

MSG_INTRO = '\nWelcome to the OSDU CLI! This command will guide you through ' \
            'setting some default values.\n'
MSG_CLOSING = '\nYou\'re all set! Here are some commands to try:\n' \
              ' $ osducli status\n' \
              ' $ osducli list records\n'

MSG_GLOBAL_SETTINGS_LOCATION = 'Your settings can be found at {}'

MSG_HEADING_CURRENT_CONFIG_INFO = 'Your current configuration is as follows:'
MSG_HEADING_ENV_VARS = '\nEnvironment variables:'

MSG_PROMPT_CONFIG = '\nWhat config file do you want to use as the default?'
MSG_PROMPT_MANAGE_GLOBAL = '\nDo you wish to change your settings?'
MSG_PROMPT_GLOBAL_OUTPUT = '\nWhat default output format would you like?'
MSG_PROMPT_SERVER = '\nOSDU API Server []: '
MSG_PROMPT_FILE_URL = '\nFile API path []: '
MSG_PROMPT_SCHEMA_URL = '\nSchema API path []: '
MSG_PROMPT_SEARCH_URL = '\nSearch API path []: '
MSG_PROMPT_STORAGE_URL = '\nStorage API path []: '
MSG_PROMPT_UNIT_URL = '\nUnit API path []: '
MSG_PROMPT_WORKFLOW_URL = '\nWorkflow API path []: '

MSG_PROMPT_DATA_PARTITION = '\nData partition name []: '
MSG_PROMPT_LEGAL_TAG = '\nManifest legal tag []: '
MSG_PROMPT_ACL_VIEWER = '\nacl viewer []: '
MSG_PROMPT_ACL_OWNER = '\nacl owner []: '

MSG_PROMPT_AUTHENTICATION_MODE = '\nHow will you authenticate?'
MSG_PROMPT_AUTHORITY = '\nAuthority []: '
MSG_PROMPT_SCOPES = '\nScopes []: '
MSG_PROMPT_TOKEN_ENDPOINT_URL = '\nAuthentication token endpoint url []: '
MSG_PROMPT_REFRESH_TOKEN = '\nRefresh token []: '
MSG_PROMPT_CLIENT_ID = '\nClient id []: '
MSG_PROMPT_CLIENT_SECRET = '\nClient secret []: '
