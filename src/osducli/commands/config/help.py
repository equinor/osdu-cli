# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Help documentation for commands."""

from knack.help_files import helps

# If the parameter name doesn't match the actual parameter name,
# no information will be provided in the help page

# To keep newlines in the help documentation, follow this format:
# long-summary: |
#    Following are the ...
#    1. text
#    2. text

helps['config'] = """
    type: group
    short-summary: Manage configuration
"""

helps['config update'] = """
    type: command
    short-summary: Update configuration values. This command is interactive.
    long-summary: Update configuration values within the currently active configuration file.
        You can specify key and value arguments to update specific entries rather than the whole list.
    parameters:
        - name: --key
          type: string
          short-summary: Optional name of a specific key within the configuration file to update.
        - name: --value
          type: string
          short-summary: If --key is specified then the value that you would like to set.
"""

helps['config set-default'] = """
    type: command
    short-summary: Set which configuration to use by default.
"""
