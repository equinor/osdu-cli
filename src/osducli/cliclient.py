# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Useful functions."""

import os
import sys
from configparser import NoOptionError, NoSectionError
from functools import wraps
from typing import Tuple, Union
from urllib.parse import urljoin

import requests
from osdu.client import OsduClient
from osdu.identity import OsduMsalInteractiveCredential, OsduTokenCredential
from requests.models import HTTPError

from osducli.config import (
    CLI_CONFIG_DIR,
    CONFIG_AUTHENTICATION_AUTHORITY,
    CONFIG_AUTHENTICATION_MODE,
    CONFIG_AUTHENTICATION_SCOPES,
    CONFIG_CLIENT_ID,
    CONFIG_CLIENT_SECRET,
    CONFIG_DATA_PARTITION_ID,
    CONFIG_REFRESH_TOKEN,
    CONFIG_SERVER,
    CONFIG_TOKEN_ENDPOINT,
    CLIConfig,
)
from osducli.log import get_logger
from osducli.util.exceptions import CliError

MSG_JSON_DECODE_ERROR = (
    "Unable to decode the response. Try running again with the --debug command line argument for"
    " more information"
)
MSG_HTTP_ERROR = (
    "Unable to access the api. Try running again with the --debug command line argument for"
    " more information"
)

logger = get_logger(__name__)


def handle_cli_exceptions(function):
    """Decorator to provide common cli error handling"""

    @wraps(function)
    def decorated(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPError as ex:
            logger.error(MSG_HTTP_ERROR)
            logger.error("Error (%s) - %s", ex.response.status_code, ex.response.reason)
        except CliError as ex:
            logger.error("Error %s", ex.message)
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.debug(ex)
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Configuration missing from config ('%s'). Run 'osducli config update'", ex.args[0]
            )
        sys.exit(1)

    return decorated


class CliOsduClient(OsduClient):
    """Specific class for use from the CLI that provides common error handling, use of configuration
    and messaging

    Args:
        OsduClient ([type]): [description]
    """

    def __init__(self, config: CLIConfig):
        """Setup the new client

        Args:
            config (CLIConfig): cli configuration
        """

        self.config = config

        try:
            # required
            server = config.get("core", CONFIG_SERVER)
            data_partition = config.get("core", CONFIG_DATA_PARTITION_ID)
            retries = config.getint("core", "retries", 0)
            authentication_mode = config.get("core", CONFIG_AUTHENTICATION_MODE)

            if authentication_mode == "refresh_token":
                client_id = config.get("core", CONFIG_CLIENT_ID)
                token_endpoint = config.get("core", CONFIG_TOKEN_ENDPOINT, None)
                refresh_token = config.get("core", CONFIG_REFRESH_TOKEN, None)
                client_secret = config.get("core", CONFIG_CLIENT_SECRET, None)
                credentials = OsduTokenCredential(
                    client_id, token_endpoint, refresh_token, client_secret
                )
            elif authentication_mode == "msal_interactive":
                client_id = config.get("core", CONFIG_CLIENT_ID)
                authority = config.get("core", CONFIG_AUTHENTICATION_AUTHORITY, None)
                scopes = config.get("core", CONFIG_AUTHENTICATION_SCOPES, None)
                cache_path = os.path.join(CLI_CONFIG_DIR, "msal_token_cache.bin")
                credentials = OsduMsalInteractiveCredential(
                    client_id, authority, scopes, cache_path
                )
            else:
                logger.error(
                    "Unknown type of authentication mode %s. Run 'osducli config update'.",
                    authentication_mode,
                )
                sys.exit(2)

            super().__init__(server, data_partition, credentials, retries)
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Authentication information missing from config ('%s'). Run 'osducli config update'",
                ex.args[0],
            )
            sys.exit(1)

    def _url_from_config(self, config_url_key: str, url_extra_path: str) -> str:
        """Construct a url using values from configuration"""
        unit_url = self.config.get("core", config_url_key)
        url = urljoin(self.server_url, unit_url) + url_extra_path
        return url

    def cli_get(
        self, config_url_key: str, url_extra_path: str, ok_status_codes: list = None
    ) -> requests.Response:
        """[summary]

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            ok_status_codes (list, optional): Status codes for successful call. Defaults to [200].
        """
        url = self._url_from_config(config_url_key, url_extra_path)
        if ok_status_codes is None:
            ok_status_codes = [200]
        response = self.get(url)
        if response.status_code not in ok_status_codes:
            raise HTTPError(response=response)
        return response

    def cli_get_returning_json(self, config_url_key: str, url_extra_path: str) -> dict:
        """[summary]

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
        """
        response = self.cli_get(config_url_key, url_extra_path)
        try:
            return response.json()
        except HTTPError as ex:
            logger.error(MSG_HTTP_ERROR)
            logger.error("Error (%s) - %s", ex.response.status_code, ex.response.reason)
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.debug(ex)
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Configuration missing from config ('%s'). Run 'osducli config update'", ex.args[0]
            )

        sys.exit(1)

    def cli_post_returning_json(
        self,
        config_url_key: str,
        url_extra_path: str,
        data: Union[str, dict],
        ok_status_codes: list = None,
    ):
        """[summary]

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            data (Union[str, dict]): json data as string or dict to send as the body
            ok_status_codes (list, optional): Status codes indicating successful call. Defaults to [200].

        Returns:
            [type]: [description]
        """
        try:
            url = self._url_from_config(config_url_key, url_extra_path)
            return self.post_returning_json(url, data, ok_status_codes)
        except HTTPError as ex:
            logger.error(MSG_HTTP_ERROR)
            logger.debug(ex.response.text)
            logger.error("Error (%s) - %s", ex.response.status_code, ex.response.reason)
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.debug(ex)
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Configuration missing from config ('%s'). Run 'osducli config update'", ex.args[0]
            )

        sys.exit(1)

    def cli_delete(
        self,
        config_url_key: str,
        url_extra_path: str,
        ok_status_codes: list = None,
    ):
        """[summary]

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            data (Union[str, dict]): json data as string or dict to send as the body
            ok_status_codes (list, optional): Status codes indicating successful call. Defaults to [200].

        Returns:
            [type]: [description]
        """
        try:
            url = self._url_from_config(config_url_key, url_extra_path)
            self.delete(url, ok_status_codes)
            return
        except HTTPError as ex:
            logger.error(MSG_HTTP_ERROR)
            logger.error("Error (%s) - %s", ex.response.status_code, ex.response.reason)
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.debug(ex)
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Configuration missing from config ('%s'). Run 'osducli config update'", ex.args[0]
            )

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

    def cli_put(
        self,
        url: str,
        # config_url_key: str,
        # url_extra_path: str,
        filepath: str,
    ) -> Tuple[requests.Response, dict]:
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
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Configuration missing from config ('%s'). Run 'osducli config update'", ex.args[0]
            )

        sys.exit(1)
