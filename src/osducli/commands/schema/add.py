# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Version command"""

import json

import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_SCHEMA_URL
from osducli.log import get_logger
from osducli.util.exceptions import CliError
from osducli.util.file import get_files_from_path

logger = get_logger(__name__)


# click entry point
@click.command()
@click.option(
    "-p",
    "--path",
    help="Path to a schema or schemas to add.",
    required=True,
)
@click.option(
    "-k",
    "--kind",
    help="Kind of the schema.",
    required=True,
)
@click.option(
    "--status",
    help="Status of the schema.",
    default="DEVELOPMENT",
    show_default=True,
)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, path: str, kind: str, status: str):
    """Add a schema"""
    return add_schema(state, path, kind, status)


# pylint: disable=too-many-locals
def add_schema(state: State, path: str, kind: str, status: str) -> dict:
    """Add schemas to OSDU

    Args:
        state (State): Global state
        path (str): Path to a schema or schemas to add.
        kind (str): Kind of the schema.
        status (str): Status of the schema.

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)
    url = "schema"

    files = get_files_from_path(path)
    logger.debug("Files list: %s", files)

    kind_parts = kind.split(":")
    if len(kind_parts) != 4:
        raise CliError(
            f"Kind '{kind}' is not in the correct format 'authority:source:entity:v:v:v'"
        )
    authority = kind_parts[0]
    source = kind_parts[1]
    entity = kind_parts[2]
    version = kind_parts[3].split(".")
    if len(version) != 3:
        raise CliError(
            f"Kind '{kind}' is not in the correct format 'authority:source:entity:v:v:v'"
        )
    version_major = version[0]
    version_minor = version[1]
    version_patch = version[2]

    responses = []
    for filepath in files:
        if filepath.endswith(".json"):
            with open(filepath) as file:
                data_object = json.load(file)

                logger.info("Processing file %s.", filepath)

                request_data = {
                    "schemaInfo": {
                        "schemaIdentity": {
                            "authority": authority,
                            "source": source,
                            "entityType": entity,
                            "schemaVersionMajor": version_major,
                            "schemaVersionMinor": version_minor,
                            "schemaVersionPatch": version_patch,
                        },
                        "status": status,
                    },
                    "schema": data_object,
                }

                response_json = connection.cli_post_returning_json(
                    CONFIG_SCHEMA_URL, url, request_data, [200, 201]
                )
                responses.append(response_json)

    return responses
