# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Help documentation for unit commands."""

from knack.help_files import helps


helps['unit'] = """
    type: group
    short-summary: Working with the Unit API
"""

# the pipe in long-summary preserves the newlines.
helps['unit list'] = """
    type: command
    short-summary: List units.
"""
