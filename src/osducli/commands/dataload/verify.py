# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Dataload verify command"""

import json

import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_SEARCH_URL, CLIConfig
from osducli.log import get_logger
from osducli.util.file import get_files_from_path

logger = get_logger(__name__)


# click entry point
@click.command()
@click.option(
    "-p",
    "--path",
    help="Path to a file or files to check.",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True),
    required=True,
)
@click.option("-b", "--batch", help="Batch size.", type=int, default=200, show_default=True)
@click.option(
    "--batch-across-files",
    is_flag=True,
    default=True,
    help="Create batches across files for speed.",
    show_default=True,
)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, path: str, batch: int = 200, batch_across_files=True):
    """Verify if records exist in OSDU.

    Note that this doesn't support versioning - success indicates that
    a record is found, although there is no check of the contents so it could be an older version if you have
    done multiple uploads of the same item with different content."""
    return verify(state, path, batch, batch_across_files)


def _create_search_query(record_ids):
    final_query = " OR ".join('"' + x + '"' for x in record_ids)
    final_query = f"id:({final_query})"

    return {
        "kind": "*:*:*:*.*.*",
        "limit": 10000,
        "returnedFields": ["id"],
        "offset": 0,
        "query": final_query,
    }


def _verify_ids(config: CLIConfig, record_ids):
    success = []
    failed = []
    search_query = _create_search_query(record_ids)
    logger.debug("search query %s", json.dumps(search_query))

    connection = CliOsduClient(config)
    response_json = connection.cli_post_returning_json(
        CONFIG_SEARCH_URL, "query?limit=10000", search_query
    )

    logger.debug("search response %s", response_json)
    ingested_records = response_json.get("results")

    for ingested_record in ingested_records:
        success.append(ingested_record.get("id"))

    failed = [x for x in record_ids if x not in success]
    if len(failed) > 0:
        logger.debug(
            "Checked %i records. Could not find %i records with Ids: %s",
            len(record_ids),
            len(failed),
            failed,
        )

    return success, failed


def batch_verify(config, batch_size, ids_to_verify, success, failed, process_all_ids=False):
    """Verify a list of id's in batches"""
    while len(ids_to_verify) >= batch_size or (process_all_ids and len(ids_to_verify) > 0):
        total_size = len(ids_to_verify)
        batch_size = min(batch_size, total_size)
        current_batch = ids_to_verify[:batch_size]
        del ids_to_verify[:batch_size]
        logger.debug(
            "Processing batch - total %i, batch size %i, remaining %i",
            total_size,
            len(current_batch),
            len(ids_to_verify),
        )
        _s, _f = _verify_ids(config, current_batch)

        success.extend(_s)
        failed.extend(_f)


def verify(
    state: State, path: str, batch_size: int, batch_across_files: bool
) -> dict:  # noqa: C901 pylint: disable=R0912
    """Verify if records exist in OSDU.

    Args:
        state (State): Global state
        path (str): Path to a file containing run ids to get status of
        batch (int): Batch size
        batch_across_files (bool): Create batches across files for speed

    Returns:
        dict: Response from service
    """
    files = get_files_from_path(path)
    logger.debug("Files list: %s", files)

    success = []
    failed = []
    ids_to_verify = []
    for filepath in files:
        if filepath.endswith(".json"):
            with open(filepath) as file:
                data_object = json.load(file)

                logger.info("Processing file %s.", filepath)

                if not data_object:
                    logger.error("Error with file %s. File is empty.", filepath)

                elif "ReferenceData" in data_object:
                    ingested_data = data_object["ReferenceData"]

                elif "MasterData" in data_object:
                    ingested_data = data_object["MasterData"]

                for ingested_datum in ingested_data:
                    if "id" in ingested_datum:
                        ids_to_verify.append(ingested_datum.get("id"))

                batch_verify(
                    state.config, batch_size, ids_to_verify, success, failed, not batch_across_files
                )

    # If batching across files then there might be records here so clear those.
    if len(ids_to_verify) > 0:
        logger.debug("Searching remaining records with batch size %s", len(ids_to_verify))
        batch_verify(state.config, batch_size, ids_to_verify, success, failed, True)

    if len(failed) == 0:
        print(
            f"All {len(success)} records exist in OSDU.",
        )
    else:
        logger.info("Number of Records that exist in OSDU: %s", len(success))
        logger.info("%i Record IDs that do not exist: %s", len(failed), failed)
