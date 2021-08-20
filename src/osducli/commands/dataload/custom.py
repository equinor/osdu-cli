# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom commands for the Service Fabric container support"""

import os
import json
import sys
import time
from knack.log import get_logger
from osducli.config import get_config_value, CONFIG_WORKFLOW_URL
from osducli.connection import CliOsduConnection

START_TIME = "startTimeStamp"
END_TIME = "endTimeStamp"
STATUS = "status"
RUN_ID = "runId"
TIME_TAKEN = "timeTaken"
FINISHED = "finished"
FAILED = "failed"

logger = get_logger(__name__)


def _populate_request_body(data, data_type):
    request = {
        "executionContext": {
            "Payload": {
                "AppKey": "test-app",
                "data-partition-id": get_config_value("data-partition-id", "core")
            },
            "manifest": {
                "kind": "osdu:wks:Manifest:1.0.0",
                data_type: data
            }
        }
    }
    logger.info("Request to be sent %s", request)
    return request


def _add_metadata(data):
    for datum in data:
        _update_legal_and_acl_tags(datum)
    return data


def _update_legal_and_acl_tags(datum):
    datum["legal"]["legaltags"] = [get_config_value("legal_tag", "core")]
    datum["legal"]["otherRelevantDataCountries"] = ["US"]
    datum["acl"]["viewers"] = [get_config_value("acl_viewer", "core")]
    datum["acl"]["owners"] = [get_config_value("acl_owner", "core")]


def ingest(path: str, runid_log: str = None, batch_size=1):  # is_wpc=False, file_location_map=""):
    """Ingest files into OSDU"""

    allfiles = []
    if os.path.isfile(path):
        allfiles = [path]

    # Recursive traversal of files and subdirectories of the root directory and files processing
    for root, _, files in os.walk(path):
        logger.info("Files list: %s", files)
        for file in files:
            allfiles.append(os.path.join(root, file))

    runids = _ingest_files(allfiles, runid_log, batch_size)

    return runids


def _ingest_files(allfiles, runid_log, batch_size):  # noqa: C901 pylint: disable=R0912
    logger.info("Files list: %s", allfiles)
    runids = []
    runid_log_handle = None
    try:
        if runid_log is not None:
            # clear existing logs
            runid_log_handle = open(runid_log, 'w')  # pylint: disable=R1732

        cur_batch = 0
        data_objects = []
        for filepath in allfiles:
            if filepath.endswith(".json"):
                with open(filepath) as file:
                    data_object = json.load(file)

            if not data_object:
                logger.error("Error with file %s. File is empty.", filepath)
            elif "ReferenceData" in data_object and len(data_object["ReferenceData"]) > 0:
                object_to_ingest = _add_metadata(data_object["ReferenceData"])
                data_type = "ReferenceData"
            elif "MasterData" in data_object and len(data_object["MasterData"]) > 0:
                object_to_ingest = _add_metadata(data_object["MasterData"])
                data_type = "MasterData"
            elif "Data" in data_object:
                data_type = "Data"
                # if file_location_map is None or len(file_location_map) == 0:
                raise Exception('File Location Map file path is required for Work-Product data ingestion')
                # object_to_ingest = update_work_products_metadata(data_object["Data"], file_location_map)

            data_objects += object_to_ingest
            cur_batch += len(object_to_ingest)

            if cur_batch >= batch_size:
                logger.info("Sending Request with batch size %s", cur_batch)
                _ingest_send_batch(runids, runid_log_handle, data_objects, data_type)
                cur_batch = 0
                data_objects = []
            else:
                logger.info("Current batch size after process %s is %s. Reading more files..", filepath, cur_batch)

        if cur_batch > 0:
            logger.info("Ingesting remaining records %s", cur_batch)
            _ingest_send_batch(runids, runid_log_handle, data_objects, data_type)
    finally:
        if runid_log is not None:
            runid_log_handle.close()
    return runids


def _ingest_send_batch(runids, runid_log_handle, data_objects, data_type):
    request_data = _populate_request_body(data_objects, data_type)
    connection = CliOsduConnection()
    _, response_json = connection.post_json_returning_json(CONFIG_WORKFLOW_URL,
                                                           'workflow/Osdu_ingest/workflowRun',
                                                           request_data)
    runid = response_json.get('runId')
    logger.info("Returned runID: %s", runid)
    runid_log_handle.write(f'{runid}\n')
    runids.append(runid)


def _status_check(run_id_list: list):
    logger.debug("list of run-ids: %s", run_id_list)

    results = []
    for run_id in run_id_list:
        connection = CliOsduConnection()
        response_json = connection.cli_get_as_json(CONFIG_WORKFLOW_URL, 'workflow/Osdu_ingest/workflowRun/' + run_id)
        if response_json is not None:
            run_status = response_json.get(STATUS)
            if run_status == "running":
                results.append({
                    RUN_ID: run_id,
                    STATUS: run_status})
            else:
                time_taken = response_json.get(END_TIME) - response_json.get(START_TIME)
                results.append({
                    RUN_ID: run_id,
                    END_TIME: response_json.get(END_TIME),
                    START_TIME: response_json.get(START_TIME),
                    STATUS: run_status,
                    TIME_TAKEN: time_taken / 1000})
        else:
            results.append({
                RUN_ID: run_id,
                STATUS: "Unable To fetch status"})

    return results


def status(runid: str = None, runid_log: str = None, wait: bool = False):
    """Get status of workflow runs"""
    runids = []
    if runid is not None:
        runids = [runid]
    elif runid_log is not None:
        with open(runid_log) as handle:
            runids = [run_id.rstrip() for run_id in handle]
    else:
        logger.error("Specify either runid or runid_log")
        sys.exit(1)

    results = _status_check(runids)

    if wait:
        # parse the results to see if the ingestion is complete.
        while True:
            ingestion_complete = True
            for result in results:
                if result.get("status") == "running":
                    ingestion_complete = False
                    logger.debug("Not all records finished. Checking again in 60s. Tried upto %s and found running",
                                 result.get("RunId"))
                    break

            if ingestion_complete:
                break

            time.sleep(60)  # 60 seconds sleep.
            results = _status_check(runids)  # recheck the status.

    return results


def _verify_ids(record_ids):
    success = []
    failed = []
    search_query = _create_search_query(record_ids)
    logger.info("search query %s", search_query)

    connection = CliOsduConnection()
    response_json = connection.cli_post_json_returning_json('search_url', 'query', search_query)

    logger.info("search response %s", response_json)
    ingested_records = response_json.get("results")

    for ingested_record in ingested_records:
        success.append(ingested_record.get("id"))

    failed = [x for x in record_ids if x not in success]
    logger.info("Failed to ingest Records %i with Ids: %s", len(failed), failed)

    return success, failed


def _create_search_query(record_ids):
    final_query = " OR ".join("\"" + x + "\"" for x in record_ids)
    return {
        "kind": "*:*:*:*.*.*",
        "returnedFields": ["id"],
        "offset": 0,
        "query": final_query
    }


def verify(path: str, batch_size: int = 1):  # noqa: C901 pylint: disable=R0912
    """Verify if records exist in OSDU. Note that this doesn't support versioning - success indicated that
    a record is found, although there is no check of the contents so it could be an older version if you have
    done multiple uploads of the same item with different content.
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
            _s, _f = _verify_ids(record_ids)
            success += _s
            failed += _f
            cur_batch = 0
            record_ids = []
        else:
            logger.info("Current batch size after process %s is %s. Reading more files..", filepath, cur_batch)

    if cur_batch > 0:
        logger.info("Searching remaining records with batch size %s", cur_batch)
        _s, _f = _verify_ids(record_ids)
        success += _s
        failed += _f

    if len(failed) == 0:
        print(f"All {len(success)} records exist in OSDU.", )
    else:
        logger.info("Number of Records that exist in OSDU: %s", len(success))
        logger.info("Record IDs that could not be ingested")
        print(failed)
    # logger.info(pformat(failed))


def list_workflows():
    """[summary]

    Returns:
        [type]: [description]
    """
    print("TODO: Should perhaps be in a workflow category")
    connection = CliOsduConnection()
    response_json = connection.cli_get_as_json(CONFIG_WORKFLOW_URL, 'workflow?prefix=')
    return response_json
