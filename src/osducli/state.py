# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Read and modify state related to the CLI"""

import os
from knack.config import CLIConfig

# knack CLIConfig has all the functionality needed to keep track of state, so we are using that
# here to prevent code duplication. We are using CLIConfig to create a file called 'state' to
# track states associated with osducli, such as the last time osducli version was checked.

# Default names
CLI_NAME = 'osducli'
SF_CLI_STATE_DIR = os.path.expanduser(os.path.join('~', '.{0}'.format(CLI_NAME)))
STATE_FILE_NAME = 'state'

# Format: Year, month, day, hour, minute, second, microsecond
DATETIME_FORMAT = "Year %Y Month %m Day %d %H:%M:%S:%f"


def get_state_path():
    """
    Returns the path of where the state file of osducli is stored.
    :return: str
    """

    # This is the same as
    # self.config_path = os.path.join(self.config_dir, CLIConfig._CONFIG_FILE_NAME)
    return CLIConfig(SF_CLI_STATE_DIR, CLI_NAME, 'state').config_path


def get_state_value(name, fallback=None):
    """Gets a state entry by name.

    In the case where the state entry name is not found, will use fallback value."""

    cli_config = CLIConfig(SF_CLI_STATE_DIR, CLI_NAME, 'state')

    return cli_config.get('core', name, fallback)


def set_state_value(name, value):
    """
    Set a state entry with a specified a value.

    :param name: (str) name of the state
    :param value: (str) value of the state
    :return: None
    """

    cli_config = CLIConfig(SF_CLI_STATE_DIR, CLI_NAME, 'state')
    cli_config.set_value('core', name, value)


def get_default_config_file():
    """Get the default config file.

    Return None if the value does not exist in state"""

    # pylint: disable= protected-access
    # TO DO Fix properly
    return get_state_value('default_config', CLIConfig._DEFAULT_CONFIG_FILE_NAME)


def set_default_config_file(default_config: str = None):
    """Set the default config file.

    :param custom_time: For testing only. Expects UTC, but without time zone information.
    :type custom_time: datetime.datetime object"""

    set_state_value('default_config', default_config)
