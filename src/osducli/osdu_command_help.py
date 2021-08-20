# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""TODO: Add module docstring."""

from knack.help import CLIHelp

from knack.help_files import helps

# Need to import so global help dict gets updated
import osducli.commands.dataload.help  # noqa: F401; pylint: disable=unused-import
import osducli.commands.config.help  # noqa: F401; pylint: disable=unused-import
import osducli.commands.list.help  # noqa: F401; pylint: disable=unused-import
import osducli.commands.status.help  # noqa: F401; pylint: disable=unused-import
import osducli.commands.unit.help  # noqa: F401; pylint: disable=unused-import
import osducli.commands.version.help  # noqa: F401; pylint: disable=unused-import

WELCOME_MESSAGE = r"""
 ___  ___  ___  _ _
| . |/ __]| . \| | |
| | |\__ \| | || | |
`___'[___/|___/ \__|

Welcome to the OSDU CLI!
Note: This is currently a work in progress. Please share ideas / issues on the git page.

Use `osducli --version` to display the current version.

Usage:
  osdu [command]

Available Commands:
"""

# main help team
helps[''] = """
    type: group
    short-summary: Commands for managing OSDU.
    long-summary: Commands follow the noun-verb pattern. See subgroups for more
        information.
"""


class OsduCommandHelp(CLIHelp):
    """OSDU CLI help loader"""

    def __init__(self, cli_ctx=None):
        super(OsduCommandHelp, self).__init__(cli_ctx=cli_ctx, welcome_message=WELCOME_MESSAGE)
