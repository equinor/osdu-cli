# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Dataload status command"""

import sys
import time

import click

from osducli.click_cli import State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_WORKFLOW_URL, CLIConfig
from osducli.log import get_logger

START_TIME = "startTimeStamp"
END_TIME = "endTimeStamp"
STATUS = "status"
RUN_ID = "runId"
TIME_TAKEN = "timeTaken"
FINISHED = "finished"
FAILED = "failed"

logger = get_logger(__name__)


# click entry point
@click.command()
@click.option("-r", "--runid", help="Runid to query status of.")
@click.option(
    "-rl",
    "--runid-log",
    help="Path to a file containing run ids to get status of (see dataload ingest -h).",
)
@click.option("-w", "--wait", help="Whether to wait for runs to complete.", is_flag=True)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, runid: str = None, runid_log: str = None, wait: bool = False):
    """Get status of workflow runs."""
    return status(state, runid, runid_log, wait)


def _status_check(config: CLIConfig, run_id_list: list):
    logger.debug("list of run-ids: %s", run_id_list)

    results = []
    for run_id in run_id_list:
        connection = CliOsduClient(config)
        response_json = connection.cli_get_returning_json(
            CONFIG_WORKFLOW_URL, "workflow/Osdu_ingest/workflowRun/" + run_id
        )
        if response_json is not None:
            run_status = response_json.get(STATUS)
            if run_status == "running":
                results.append({RUN_ID: run_id, STATUS: run_status})
            else:
                time_taken = response_json.get(END_TIME) - response_json.get(START_TIME)
                results.append(
                    {
                        RUN_ID: run_id,
                        END_TIME: response_json.get(END_TIME),
                        START_TIME: response_json.get(START_TIME),
                        STATUS: run_status,
                        TIME_TAKEN: time_taken / 1000,
                    }
                )
        else:
            results.append({RUN_ID: run_id, STATUS: "Unable To fetch status"})
    print(results)
    return results


def status(state: State, runid: str = None, runid_log: str = None, wait: bool = False) -> dict:
    """Get status of workflow runs

    Args:
        state (State): Global state
        group (str): Email address of the group

    Returns:
        dict: Response from service
    """
    runids = []
    if runid is not None:
        runids = [runid]
    elif runid_log is not None:
        with open(runid_log) as handle:
            runids = [run_id.rstrip() for run_id in handle]
    else:
        logger.error("Specify either runid or runid_log")
        sys.exit(1)

    results = _status_check(state.config, runids)

    if wait:
        # parse the results to see if the ingestion is complete.
        while True:
            ingestion_complete = True
            for result in results:
                if result.get("status") == "running":
                    ingestion_complete = False
                    logger.debug(
                        "Not all records finished. Checking again in 60s. Tried upto %s and found running",
                        result.get("RunId"),
                    )
                    break

            if ingestion_complete:
                break

            time.sleep(60)  # 60 seconds sleep.
            results = _status_check(state.config, runids)  # recheck the status.

    return results
