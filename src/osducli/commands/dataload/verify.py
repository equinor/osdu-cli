# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Dataload verify command"""

import json
import os

import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_SEARCH_URL, CLIConfig
from osducli.log import get_logger

logger = get_logger(__name__)


# click entry point
@click.command()
@click.option(
    "-p",
    "--path",
    help="Path to a file containing run ids to get status of (see dataload ingest -h).",
    required=True,
)
@click.option("-b", "--batch", help="Batch size.", type=int, default=1)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, path: str, batch: int = 1):
    """Verify if records exist in OSDU.

    Note that this doesn't support versioning - success indicates that
    a record is found, although there is no check of the contents so it could be an older version if you have
    done multiple uploads of the same item with different content."""
    return verify(state, path, batch)


def _verify_ids(config: CLIConfig, record_ids):
    success = []
    failed = []
    search_query = _create_search_query(record_ids)
    logger.info("search query %s", search_query)

    connection = CliOsduClient(config)
    response_json = connection.cli_post_returning_json(CONFIG_SEARCH_URL, "query", search_query)

    logger.info("search response %s", response_json)
    ingested_records = response_json.get("results")

    for ingested_record in ingested_records:
        success.append(ingested_record.get("id"))

    failed = [x for x in record_ids if x not in success]
    logger.info("Failed to ingest Records %i with Ids: %s", len(failed), failed)

    return success, failed


def _create_search_query(record_ids):
    final_query = " OR ".join('"' + x + '"' for x in record_ids)
    return {"kind": "*:*:*:*.*.*", "returnedFields": ["id"], "offset": 0, "query": final_query}


def verify(state: State, path: str, batch_size: int) -> dict:  # noqa: C901 pylint: disable=R0912
    """Verify if records exist in OSDU.

    Args:
        state (State): Global state
        path (str): Path to a file containing run ids to get status of
        batch (int): Batch size

    Returns:
        dict: Response from service
    """
    allfiles = []
    if os.path.isfile(path):
        allfiles = [path]

    # Recursive traversal of files and subdirectories of the root directory and files processing
    for root, _, files in os.walk(path):
        logger.info("Files list: %s", files)
        for file in files:
            allfiles.append(os.path.join(root, file))

    success = []
    failed = []
    logger.info("Files list: %s", allfiles)
    cur_batch = 0
    record_ids = []
    for filepath in allfiles:
        if filepath.endswith(".json"):
            with open(filepath) as file:
                data_object = json.load(file)

        if not data_object:
            logger.error("Error with file %s. File is empty.", filepath)

        elif "ReferenceData" in data_object:
            ingested_data = data_object["ReferenceData"]

        elif "MasterData" in data_object:
            ingested_data = data_object["MasterData"]

        for ingested_datum in ingested_data:
            if "id" in ingested_datum:
                record_ids.append(ingested_datum.get("id"))
                cur_batch += 1

        if cur_batch >= batch_size:
            logger.info("Searching records with batch size %s", cur_batch)
            _s, _f = _verify_ids(state.config, record_ids)
            success += _s
            failed += _f
            cur_batch = 0
            record_ids = []
        else:
            logger.info(
                "Current batch size after process %s is %s. Reading more files..",
                filepath,
                cur_batch,
            )

    if cur_batch > 0:
        logger.info("Searching remaining records with batch size %s", cur_batch)
        _s, _f = _verify_ids(state.config, record_ids)
        success += _s
        failed += _f

    if len(failed) == 0:
        print(
            f"All {len(success)} records exist in OSDU.",
        )
    else:
        logger.info("Number of Records that exist in OSDU: %s", len(success))
        logger.info("Record IDs that could not be ingested")
        print(failed)
    # logger.info(pformat(failed))
