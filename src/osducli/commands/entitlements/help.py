# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Help documentation for list commands."""

from knack.help_files import helps


helps['entitlements'] = """
    type: group
    short-summary: Manage entitlements
"""

helps['entitlements groups'] = """
    type: command
    short-summary: Manage Groups.
"""
helps['entitlements members'] = """
    type: command
    short-summary: Manage members.
"""

helps['entitlements members add'] = """
    type: command
    short-summary: Add members to a group
"""

helps['entitlements members list'] = """
    type: command
    short-summary: Add members in a group
"""

helps['entitlements mygroups'] = """
    type: command
    short-summary: List groups you have access to
"""
