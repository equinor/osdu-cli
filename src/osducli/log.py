# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Read and modify configuration settings related to the CLI"""

import logging
from enum import IntEnum

CLI_LOGGER_NAME = "cli"
# Add more logger names to this list so that ERROR, WARNING, INFO logs from these loggers can also be displayed
# without --debug flag.
cli_logger_names = [CLI_LOGGER_NAME]

LOG_FILE_ENCODING = "utf-8"


class CliLogLevel(IntEnum):
    """[summary]

    Args:
        IntEnum ([type]): [description]
    """

    CRITICAL = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4


def get_logger(module_name=None):
    """Get the logger for a module. If no module name is given, the current CLI logger is returned.

    Example:
        get_logger(__name__)

    :param module_name: The module to get the logger for
    :type module_name: str
    :return: The logger
    :rtype: logger
    """
    if module_name:
        logger_name = "{}.{}".format(CLI_LOGGER_NAME, module_name)
    else:
        logger_name = CLI_LOGGER_NAME
    return logging.getLogger(logger_name)
