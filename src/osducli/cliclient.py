# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Useful functions."""

import os
import sys
from configparser import NoOptionError, NoSectionError
from typing import Tuple, Union
from urllib.parse import urljoin

import requests
from knack.log import get_logger

from osdu.client import OsduClient
from osdu.identity import OsduTokenCredential, OsduMsalInteractiveCredential
from requests.models import HTTPError
from osducli.config import get_config_int, get_config_value, CLI_CONFIG_DIR
from osducli.config import (CONFIG_SERVER,
                            CONFIG_DATA_PARTITION_ID,
                            CONFIG_AUTHENTICATION_MODE,
                            CONFIG_CLIENT_ID,
                            CONFIG_TOKEN_ENDPOINT,
                            CONFIG_REFRESH_TOKEN,
                            CONFIG_CLIENT_SECRET,
                            CONFIG_AUTHENTICATION_AUTHORITY,
                            CONFIG_AUTHENTICATION_SCOPES)

MSG_JSON_DECODE_ERROR = 'Unable to decode the response. Try running again with the --debug command line argument for'\
                        ' more information'
MSG_HTTP_ERROR = 'Unable to access the api. Try running again with the --debug command line argument for'\
                 ' more information'

logger = get_logger(__name__)


class CliOsduClient(OsduClient):
    """Specific class for use from the CLI that provides common error handling, use of configuration
    and messaging

    Args:
        OsduClient ([type]): [description]
    """

    def __init__(self):
        """Setup the new client

        Args:
            server_url (str): url of the server without any path e.g. https://www.test.com
            data_partition (str): data partition name e.g. opendes
            credentials (OsduBaseCredential): credentials used for connection
            retries (int): number of retries incase of http errors (default 0 - no retries)
        """

        try:
            # required
            server = get_config_value(CONFIG_SERVER, 'core')
            data_partition = get_config_value(CONFIG_DATA_PARTITION_ID, 'core')
            retries = get_config_int("retries", "core", 0)
            authentication_mode = get_config_value(CONFIG_AUTHENTICATION_MODE, "core")

            if authentication_mode == "refresh_token":
                client_id = get_config_value(CONFIG_CLIENT_ID, "core")
                token_endpoint = get_config_value(CONFIG_TOKEN_ENDPOINT, "core", None)
                refresh_token = get_config_value(CONFIG_REFRESH_TOKEN, "core", None)
                client_secret = get_config_value(CONFIG_CLIENT_SECRET, "core", None)
                credentials = OsduTokenCredential(client_id, token_endpoint, refresh_token, client_secret)
            elif authentication_mode == "msal_interactive":
                client_id = get_config_value(CONFIG_CLIENT_ID, "core")
                authority = get_config_value(CONFIG_AUTHENTICATION_AUTHORITY, "core", None)
                scopes = get_config_value(CONFIG_AUTHENTICATION_SCOPES, "core", None)
                cache_path = os.path.join(CLI_CONFIG_DIR, 'msal_token_cache.bin')
                credentials = OsduMsalInteractiveCredential(client_id, authority, scopes, cache_path)
            else:
                logger.error("Unknown type of authentication mode %s. Run 'osducli config update'.",
                             authentication_mode)
                sys.exit(2)

            super().__init__(server, data_partition, credentials, retries)
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Authentication information missing from config ('%s'). Run 'osducli config update'", ex.args[0])
            sys.exit(1)

    def _url_from_config(self, config_url_key: str, url_extra_path: str) -> str:
        """Construct a url using values from configuration"""
        unit_url = get_config_value(config_url_key, 'core')
        url = urljoin(self.server_url, unit_url) + url_extra_path
        return url

    def cli_get(self, config_url_key: str, url_extra_path: str) -> requests.Response:
        """[summary]

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
        """
        url = self._url_from_config(config_url_key, url_extra_path)
        response = self.get(url)
        if response.status_code in [200]:
            return response

        logger.error(MSG_HTTP_ERROR)
        logger.error("Error (%s) - %s", response.status_code, response.reason)

        sys.exit(1)

    def cli_get_returning_json(self, config_url_key: str, url_extra_path: str) -> dict:
        """[summary]

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
        """
        response = self.cli_get(config_url_key, url_extra_path)
        try:
            return response.json()
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.debug(ex)

        sys.exit(1)

    def cli_post_returning_json(self, config_url_key: str, url_extra_path: str, data: Union[str, dict]):
        """[summary]

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            data (Union[str, dict]): json data as string or dict to send as the body

        Returns:
            [type]: [description]
        """
        try:
            url = self._url_from_config(config_url_key, url_extra_path)
            return self.post_returning_json(url, data)
        except HTTPError as ex:
            logger.error(MSG_HTTP_ERROR)
            logger.error("Error (%s) - %s", ex.response.status_code, ex.response.reason)
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.debug(ex)

        sys.exit(1)

        # # loop for implementing retries send process
        # retries = config.getint("CONNECTION", "retries")
        # for retry in range(retries):
        #     try:

        #         if response.status_code in DATA_LOAD_OK_RESPONSE_CODES:
        #             workflow_response = response.json()
        #             logger.info(f"Response: {workflow_response}")
        #             file_logger.info(f"{workflow_response.get('runId')}")
        #             break

        #         reason = response.text[:250]
        #         logger.error(f"Request error.")
        #         logger.error(f"Response status: {response.status_code}. "
        #                     f"Response content: {reason}.")

        #         if retry + 1 < retries:
        #             if response.status_code in BAD_TOKEN_RESPONSE_CODES:
        #                 logger.error(f"Error in Request: {headers.get('correlation-id')})")
        #             else:
        #                 time_to_sleep = config.getint("CONNECTION", "timeout")

        #                 logger.info(f"Retrying in {time_to_sleep} seconds...")
        #                 time.sleep(time_to_sleep)

        #     except (requests.RequestException, HTTPError) as exc:
        #         logger.error(f"Unexpected request error. Reason: {exc}")
        #         sys.exit(2)

    def cli_put(self,
                url: str,
                # config_url_key: str,
                # url_extra_path: str,
                filepath: str) -> Tuple[requests.Response, dict]:
        """PUT the file at the given path to the given url.
        Includes common CLI specific error handling

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            filepath (str): path to a file to PUT

        Returns:
            Tuple[requests.Response, dict]: Turle with response object and returned json
        """
        try:
            # url = CliOsduClient._url_from_config(config_url_key, url_extra_path)
            response = self.put(url, filepath)
            if response.status_code in [200]:
                return response, response.json()

            logger.error(MSG_HTTP_ERROR)
            logger.error("Error (%s) - %s", response.status_code, response.reason)
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.debug(ex)

        sys.exit(1)
