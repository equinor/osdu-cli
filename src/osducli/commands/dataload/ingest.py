# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Dataload ingest command"""

import json
import os

import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import (
    CONFIG_ACL_OWNER,
    CONFIG_ACL_VIEWER,
    CONFIG_DATA_PARTITION_ID,
    CONFIG_FILE_URL,
    CONFIG_LEGAL_TAG,
    CONFIG_WORKFLOW_URL,
    CLIConfig,
)
from osducli.log import get_logger
from osducli.util.file import get_files_from_path

logger = get_logger(__name__)


# click entry point
@click.command()
@click.option(
    "-p",
    "--path",
    help="Path to a file or files to ingest.",
    required=True,
)
@click.option("-f", "--files", help="Associated files to upload for Work-Products.")
@click.option("-b", "--batch", help="Batch size.", type=int, default=1)
@click.option(
    "-rl",
    "--runid-log",
    help="Path to a file containing run ids to get status of (see dataload ingest -h).",
)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, path: str, files: str, batch: int = 1, runid_log: str = None):
    """Ingest files into OSDU."""
    return ingest(state, path, files, batch, runid_log)


def ingest(state: State, path: str, files: str, batch_size: int = 1, runid_log: str = None) -> dict:
    """Ingest files into OSDU

    Args:
        state (State): Global state
        group (str): Email address of the group

    Returns:
        dict: Response from service
    """
    files = get_files_from_path(path)
    logger.debug("Files list: %s", files)

    runids = _ingest_files(state.config, files, files, runid_log, batch_size)
    print(runids)
    return runids


def _ingest_files(
    config: CLIConfig, allfiles, files, runid_log, batch_size
):  # noqa: C901 pylint: disable=R0912
    logger.info("Files list: %s", allfiles)
    runids = []
    runid_log_handle = None
    try:
        if runid_log is not None:
            # clear existing logs
            runid_log_handle = open(runid_log, "w")  # pylint: disable=R1732

        data_objects = []
        for filepath in allfiles:
            if filepath.endswith(".json"):
                with open(filepath) as file:
                    data_object = json.load(file)

            if not data_object:
                logger.error("Error with file %s. File is empty.", filepath)
            elif "ReferenceData" in data_object and len(data_object["ReferenceData"]) > 0:
                object_to_ingest = _update_legal_and_acl_tags_all(
                    config, data_object["ReferenceData"]
                )
                data_type = "ReferenceData"
            elif "MasterData" in data_object and len(data_object["MasterData"]) > 0:
                object_to_ingest = _update_legal_and_acl_tags_all(config, data_object["MasterData"])
                data_type = "MasterData"
            elif "Data" in data_object:
                data_type = "Data"
                object_to_ingest = _update_work_products_metadata(
                    config, data_object["Data"], files
                )

            data_objects += object_to_ingest

            _process_batch(config, batch_size, data_type, data_objects, runids, runid_log_handle)
    finally:
        if runid_log is not None:
            runid_log_handle.close()
    return runids


def _process_batch(
    config,
    batch_size,
    data_type,
    data_objects,
    runids,
    runid_log_handle,
    # process_all_ids=False,
):
    # while len(data_objects) >= batch_size or (process_all_ids and len(data_objects) > 0):
    while len(data_objects) > 0:
        total_size = len(data_objects)
        batch_size = min(batch_size, total_size)
        current_batch = data_objects[:batch_size]
        del data_objects[:batch_size]
        print(
            f"Processing batch - total {total_size}, batch size {len(current_batch)}, remaining {len(data_objects)}"
        )
        request_data = _populate_request_body(config, data_objects, data_type)
        connection = CliOsduClient(config)
        response_json = connection.cli_post_returning_json(
            CONFIG_WORKFLOW_URL, "workflow/Osdu_ingest/workflowRun", request_data
        )
        runid = response_json.get("runId")
        logger.info("Returned runID: %s", runid)
        if runid_log_handle:
            runid_log_handle.write(f"{runid}\n")
        runids.append(runid)


def _populate_request_body(config: CLIConfig, data, data_type):
    request = {
        "executionContext": {
            "Payload": {
                "AppKey": "test-app",
                "data-partition-id": config.get("core", CONFIG_DATA_PARTITION_ID),
            },
            "manifest": {"kind": "osdu:wks:Manifest:1.0.0", data_type: data},
        }
    }
    logger.debug("Request to be sent %s", request)
    return request


def _upload_file(config: CLIConfig, filepath):
    connection = CliOsduClient(config)
    initiate_upload_response_json = connection.cli_get_returning_json(
        CONFIG_FILE_URL, "files/uploadURL"
    )

    location = initiate_upload_response_json.get("Location")
    if location:
        signed_url_for_upload = location.get("SignedURL")
        file_source = location.get("FileSource")
        connection.cli_put(signed_url_for_upload, filepath)

        # generated_file_id = upload_metadata_response_json.get("id")
        # logger.info("%s is uploaded with file id %s with file source %s", filepath, generated_file_id, file_source)
        # return generated_file_id, file_source
        return file_source

    return None


def _update_work_products_metadata(config: CLIConfig, data, files):
    _update_legal_and_acl_tags(config, data["WorkProduct"])
    _update_legal_and_acl_tags_all(config, data["WorkProductComponents"])
    _update_legal_and_acl_tags_all(config, data["Datasets"])

    # if files is specified then upload any needed data.
    if files:
        for dataset in data.get("Datasets"):
            file_source_info = (
                dataset.get("data", {}).get("DatasetProperties", {}).get("FileSourceInfo")
            )
            # only process if FileSource isn't already specified
            if file_source_info and not file_source_info.get("FileSource"):
                file_source_info["FileSource"] = _upload_file(
                    config, os.path.join(files, file_source_info["Name"])
                )
            else:
                logger.info(
                    "FileSource already especified for '%s' - skipping.", file_source_info["Name"]
                )

    # TO DO: Here we scan by name from filemap
    # with open(file_location_map) as file:
    #     location_map = json.load(file)

    # file_name = data["WorkProduct"]["data"]["Name"]
    # if file_name in location_map:
    #     file_source = location_map[file_name]["file_source"]
    #     file_id = location_map[file_name]["file_id"]

    #     # Update Dataset with Generated File Id and File Source.
    #     data["Datasets"][0]["id"] = file_id
    #     data["Datasets"][0]["data"]["DatasetProperties"]["FileSourceInfo"]["FileSource"] = file_source
    #     del data["Datasets"][0]["data"]["DatasetProperties"]["FileSourceInfo"]["PreloadFilePath"]

    #     # Update FileId in WorkProductComponent
    #     data["WorkProductComponents"][0]["data"]["Datasets"][0] = file_id
    # else:
    #     logger.warn(f"Filemap {file_name} does not exist")

    # logger.info(f"data to upload workproduct \n {data}")

    return data


def _update_legal_and_acl_tags_all(config: CLIConfig, data):
    for datum in data:
        _update_legal_and_acl_tags(config, datum)
    return data


def _update_legal_and_acl_tags(config: CLIConfig, datum):
    datum["legal"]["legaltags"] = [config.get("core", CONFIG_LEGAL_TAG)]
    datum["legal"]["otherRelevantDataCountries"] = ["US"]
    datum["acl"]["viewers"] = [config.get("core", CONFIG_ACL_VIEWER)]
    datum["acl"]["owners"] = [config.get("core", CONFIG_ACL_OWNER)]
