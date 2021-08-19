# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""TODO: Add module docstring."""

from knack import CLI


class OsduCli(CLI):
    """Extend CLI to override get_cli_version."""
    def get_cli_version(self):
        from osducli import __VERSION__
        return __VERSION__
