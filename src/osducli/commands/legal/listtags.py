# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""
import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_LEGAL_URL


@click.command()
@handle_cli_exceptions
@command_with_output(
    "legalTags[*].{Name:name,Description:description,Classification:properties.securityClassification,PersonalData:properties.personalData,Export:properties.exportClassification,Origin:properties.originator}"  # noqa: E501 pylint: disable=C0301
)
def _click_command(state: State):
    """List legal tags"""

    return records(state)


def records(state: State):
    """[summary]

    Args:
        state (State): Global state
    """
    connection = CliOsduClient(state.config)
    json_response = connection.cli_get_returning_json(CONFIG_LEGAL_URL, "legaltags")

    return json_response
