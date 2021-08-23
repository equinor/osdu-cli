# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Help documentation for list commands."""

from knack.help_files import helps


helps['list'] = """
    type: group
    short-summary: Information about OSDU contents
"""

# the pipe in long-summary preserves the newlines.
helps['list records'] = """
    type: command
    short-summary: List count of populated records.
"""
