# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Dataload ingest command"""

import json
import os

import click
import requests

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.dataload.status import check_status
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
from osducli.util.exceptions import CliError
from osducli.util.file import get_files_from_path

logger = get_logger(__name__)


# click entry point
@click.command()
@click.option(
    "-p",
    "--path",
    help="Path to a file or files to ingest.",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True),
    required=True,
)
@click.option("-f", "--files", help="Associated files to upload for Work-Products.")
@click.option("-b", "--batch", help="Batch size.", type=int, default=1, show_default=True)
@click.option(
    "-rl",
    "--runid-log",
    help="Path to a file containing run ids to get status of (see dataload ingest -h).",
)
@click.option(
    "-w", "--wait", help="Whether to wait for runs to complete.", is_flag=True, show_default=True
)
@click.option("--simulate", help="Simulate ingestion only.", is_flag=True, show_default=True)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(
    state: State,
    path: str,
    files: str,
    batch: int = 1,
    runid_log: str = None,
    wait: bool = False,
    simulate: bool = False,
):
    """Ingest files into OSDU."""
    return ingest(state, path, files, batch, runid_log, wait, simulate)


def ingest(
    state: State,
    path: str,
    files: str,
    batch_size: int = 1,
    runid_log: str = None,
    wait: bool = False,
    simulate: bool = False,
) -> dict:
    """Ingest files into OSDU

    Args:
        state (State): Global state

    Returns:
        dict: Response from service
    """
    manifest_files = get_files_from_path(path)
    logger.debug("Files list: %s", files)

    runids = _ingest_files(
        state.config, manifest_files, files, runid_log, batch_size, wait, simulate
    )
    print(runids)
    return runids


def _ingest_files(
    config: CLIConfig, manifest_files, files, runid_log, batch_size, wait, simulate
):  # noqa: C901 pylint: disable=R0912
    logger.info("Files list: %s", manifest_files)
    runids = []
    runid_log_handle = None
    try:
        if runid_log is not None and not simulate:
            # clear existing logs
            runid_log_handle = open(runid_log, "w")  # pylint: disable=R1732

        data_objects = []
        for filepath in manifest_files:
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
                    config, data_object["Data"], files, simulate
                )
                _create_and_submit(
                    config, data_type, object_to_ingest, runids, runid_log_handle, simulate
                )
                continue

            data_objects.append(object_to_ingest)

            _process_batch(
                config, batch_size, data_type, data_objects, runids, runid_log_handle, simulate
            )
    finally:
        if runid_log is not None:
            runid_log_handle.close()

    if wait and not simulate:
        logger.debug("%d batches submitted. Waiting for run status", len(runids))
        check_status(config, runids, True)
    return runids


def _process_batch(config, batch_size, data_type, data_objects, runids, runid_log_handle, simulate):
    while len(data_objects) > 0:
        total_size = len(data_objects)
        batch_size = min(batch_size, total_size)
        current_batch = data_objects[:batch_size]
        del data_objects[:batch_size]
        print(
            f"Processing batch - total {total_size}, batch size {len(current_batch)}, remaining {len(data_objects)}"
        )

        _create_and_submit(config, data_type, current_batch, runids, runid_log_handle, simulate)


def _create_and_submit(config, data_type, data, runids, runid_log_handle, simulate):
    request_data = _populate_request_body(config, data, data_type)
    if not simulate:
        connection = CliOsduClient(config)
        response_json = connection.cli_post_returning_json(
            CONFIG_WORKFLOW_URL, "workflow/Osdu_ingest/workflowRun", request_data
        )
        logger.debug("Request to be sent %s", response_json)

        runid = response_json.get("runId")
        logger.info("Returned runID: %s", runid)
        if runid_log_handle:
            runid_log_handle.write(f"{runid}\n")
        runids.append(runid)


def _populate_request_body(config: CLIConfig, data, data_type):
    request = {
        "executionContext": {
            "Payload": {
                "AppKey": "osdu-cli",
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

        headers = {"Content-Type": "application/octet-stream", "x-ms-blob-type": "BlockBlob"}
        with open(filepath, "rb") as file_handle:
            response = requests.put(signed_url_for_upload, data=file_handle, headers=headers)
            if response.status_code not in [200, 201]:
                raise CliError(f"({response.status_code}) {response.text[:250]}")

        # generated_file_id = upload_metadata_response_json.get("id")
        # logger.info("%s is uploaded with file id %s with file source %s", filepath, generated_file_id, file_source)
        # return generated_file_id, file_source
        return file_source

    raise CliError(f"No upload location returned: {initiate_upload_response_json}")


def _update_work_products_metadata(config: CLIConfig, data, files, simulate):
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
                if not simulate:
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

    # logger.debug(f"data to upload workproduct \n {data}")
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
