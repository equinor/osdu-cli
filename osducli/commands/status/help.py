# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Help documentation for status commands."""

from knack.help_files import helps

# If the parameter name doesn't match the actual parameter name,
# no information will be provided in the help page

# To keep newlines in the help documentation, follow this format:
# long-summary: |
#    Following are the ...
#    1. text
#    2. text

helps['status'] = """
    type: command
    short-summary: Shows the status of OSDU services
"""
