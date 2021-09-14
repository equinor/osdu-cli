# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Version command"""

import sys

import click

import osducli
from osducli.click_cli import global_params
from osducli.cliclient import handle_cli_exceptions


# click entry point
@click.command()
@handle_cli_exceptions
@global_params
def _click_command(_):
    """Version information"""
    version()


def get_runtime_version() -> str:
    """Get the runtime information.

    Returns:
        str: Runtime information
    """
    import platform

    version_info = "\n\n"
    version_info += "Python ({}) {}".format(platform.system(), sys.version)
    version_info += "\n\n"
    version_info += "Python location '{}'".format(sys.executable)
    return version_info


def version():
    """Print version information to standard system out."""
    version_info = f"OSDU Cli Version {osducli.__VERSION__}"
    version_info += get_runtime_version()
    print(version_info)
