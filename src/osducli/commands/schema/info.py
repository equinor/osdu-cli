# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Version command"""

import click

from osducli.click_cli import global_params
from osducli.cliclient import handle_cli_exceptions


# click entry point
@click.command()
@handle_cli_exceptions
@global_params
def _click_command(_):
    """Coming soon"""
    print("TODO - coming soon")
