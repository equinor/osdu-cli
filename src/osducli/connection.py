# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Useful functions."""

import atexit
import json
import os
import sys
from configparser import NoOptionError, NoSectionError
from datetime import datetime
from json import loads
from typing import Tuple
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

import requests
from knack.log import get_logger

from osducli.config import get_config_int, get_config_value, SF_CLI_CONFIG_DIR
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


class OsduConnection:
    """
    Class for connecting with API's.
    """
    # def __init__(self, config, *args, **keywords):
    def __init__(self):
        # self.__config = config
        # self.__args = args
        # self.__keywords = keywords
        self.__expire_date = 0
        self._id_token = None
        self._access_token = None

        try:
            # required
            self._retries = get_config_int("retries", "core", 2)
            self._authentication_mode = get_config_value(CONFIG_AUTHENTICATION_MODE, "core")
            self._client_id = get_config_value(CONFIG_CLIENT_ID, "core")
            # token refresh specific - default to None rather than fail incase different auth
            self._token_endpoint = get_config_value(CONFIG_TOKEN_ENDPOINT, "core", None)
            self._refresh_token = get_config_value(CONFIG_REFRESH_TOKEN, "core", None)
            self._client_secret = get_config_value(CONFIG_CLIENT_SECRET, "core", None)
            # msal interactive specific - default to None rather than fail incase different auth
            self._auth_authority = get_config_value(CONFIG_AUTHENTICATION_AUTHORITY, "core", None)
            self._auth_scopes = get_config_value(CONFIG_AUTHENTICATION_SCOPES, "core", None)
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Authentication information missing from config ('%s'). Run 'osducli config update'", ex.args[0])
            sys.exit(1)

    def id_token(self):  # pylint: disable=E0213
        """
        Check expiration date and return id_token.
        """
        if datetime.now().timestamp() > self.__expire_date:
            self.refresh()
        return self._id_token

    def access_token(self):  # pylint: disable=E0213
        """
        Check expiration date and return access_token.
        """
        if datetime.now().timestamp() > self.__expire_date:
            self.refresh()
        return self._access_token

    @staticmethod
    def _refresh_refresh_token(url: str, refresh_token: str, client_id: str, client_secret: str) -> dict:
        """
        Send refresh token requests to OpenID token endpoint.

        Return dict with keys "access_token", "expires_in", "scope", "token_type", "id_token".
        """

        body = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = urlencode(body).encode("utf8")
        request = Request(url=url, data=data, headers=headers)
        try:
            with urlopen(request) as response:
                response_body = response.read()
                return loads(response_body)
        except HTTPError as ex:
            code = ex.code
            message = ex.read().decode("utf8")
            logger.error("Refresh token request failed. %s %s", code, message)
            raise

    def refresh_refresh_token(self) -> dict:
        """Refresh from refresh token.

        Returns:
            dict: Dictionary representing the returned token
        """
        for i in range(self._retries):
            # try several times if there any error
            try:
                result = self._refresh_refresh_token(
                    self._token_endpoint, self._refresh_token, self._client_id, self._client_secret)
            except HTTPError:
                if i == self._retries - 1:
                    # too many errors, raise original exception
                    raise
        return result  # You may need this when reporting a bug

    def refresh_msal_interactive(self) -> dict:
        """Refresh token using msal.

        Returns:
            dict: Dictionary representing the returned token
        """
        import msal

        # Create a preferably long-lived app instance which maintains a persistant token cache.
        cache = msal.SerializableTokenCache()
        cache_path = os.path.join(SF_CLI_CONFIG_DIR, 'msal_token_cache.bin')
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as cachefile:
                cache.deserialize(cachefile.read())
        atexit.register(lambda: open(cache_path, 'w').write(  # pylint: disable=R1732
            cache.serialize()) if cache.has_state_changed else None)

        app = msal.PublicClientApplication(
            self._client_id,
            authority=self._auth_authority,
            token_cache=cache
            )

        result = None

        # Firstly, check the cache to see if this end user has signed in before
        # accounts = app.get_accounts(username=config.get("username"))
        accounts = app.get_accounts()
        if accounts:
            logger.info("Account(s) exists in cache, probably with token too. Let's try.")
            # for a in accounts:
            #     print(a["username"])
            chosen = accounts[0]  # Assuming the end user chose this one to proceed - should change if multiple
            # Now let's try to find a token in cache for this account
            result = app.acquire_token_silent([self._auth_scopes], account=chosen)

        if not result:
            logger.info("No suitable token exists in cache. Let's get a new one from AAD.")
            print("A local browser window will be open for you to sign in. CTRL+C to cancel.")
            result = app.acquire_token_interactive(
                [self._auth_scopes],
                timeout=10,
                # login_hint=config.get("username"),  # Optional.
                # If you know the username ahead of time, this parameter can pre-fill
                # the username (or email address) field of the sign-in page for the user,
                # Often, apps use this parameter during reauthentication,
                # after already extracting the username from an earlier sign-in
                # by using the preferred_username claim from returned id_token_claims.
                # Or simply "select_account" as below - Optional. It forces to show account selector page
                prompt=msal.Prompt.SELECT_ACCOUNT
            )

        return result

    def refresh(self):
        """
        Refresh token and save them into class.
        """
        logger.info("Refreshing token.")

        result = None
        if self._authentication_mode == "refresh_token":
            result = self.refresh_refresh_token()

        elif self._authentication_mode == "msal_interactive":
            result = self.refresh_msal_interactive()

        if "preferred_username" in result:
            # TO DO: Save username for later login
            pass

        if "access_token" in result:
            self._id_token = result["id_token"]
            self._access_token = result["access_token"]
            self.__expire_date = datetime.now().timestamp() + result["expires_in"]

            logger.info("Token is refreshed.")
        else:
            print(result.get("error"))
            print(result.get("error_description"))
            print(result.get("correlation_id"))

    def get_token(self) -> str:
        """
        Refresh access or id token depending on config settings.

        :param RawConfigParser config: config that is used in calling module
        :return: token of requested type
        :rtype: str
        """

        if self._authentication_mode == "refresh_token":
            return self.access_token()
        # elif authentication_mode == "id_token":
        #     return self.id_token()
        if self._authentication_mode == "msal_interactive":
            return self.access_token()

        logger.error("Unknown type of authentication mode %s. Run 'osducli config update'.",
                     self._authentication_mode)
        sys.exit(2)

    def get_headers(self) -> dict:
        """
        Get request headers.

        :param RawConfigParser config: config that is used in calling module
        :return: dictionary with headers required for requests
        :rtype: dict
        """
        correlation_id = 'workflow-create-%s' % datetime.now().strftime('%m%d-%H%M%S')

        return {
            "Content-Type": "application/json",
            "data-partition-id": get_config_value(CONFIG_DATA_PARTITION_ID, "core"),
            "Authorization": f"Bearer {self.get_token()}",
            "correlation-id": correlation_id
        }

    def get(self, config_url_key: str, url_extra_path: str) -> requests.Response:
        """Get data from a url

        Args:
            config_url_key (str): key for the url in the config file
            url_extra_path (str): extra path to add to the url

        Returns:
            requests.Response: [description]
        """
        server = get_config_value(CONFIG_SERVER, 'core')
        unit_url = get_config_value(config_url_key, 'core')
        url = urljoin(server, unit_url) + url_extra_path

        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response

    def get_as_json(self, config_url_key: str, url_extra_path: str) -> Tuple[requests.Response, dict]:
        """Get data from the specified url in json format.

        Args:
            config_url_key (str): key for the url in the config file
            url_extra_path (str): extra path to add to the url

        Returns:
            dict: [description]
        """
        response = self.get(config_url_key, url_extra_path)
        return response, response.json()

    def post_json(self, config_url_key: str, url_extra_path: str, json_data: dict) -> requests.Response:
        """Post data to a url

        Args:
            config_url_key (str): key for the url in the config file
            url_extra_path (str): extra path to add to the url

        Returns:
            requests.Response: [description]
        """

        data = json.dumps(json_data)

        server = get_config_value(CONFIG_SERVER, 'core')
        unit_url = get_config_value(config_url_key, 'core')
        url = urljoin(server, unit_url) + url_extra_path

        headers = self.get_headers()
        logger.debug(url)
        logger.debug(data)
        response = requests.post(url, data, headers=headers)
        logger.debug(response.text)
        return response

    def post_json_returning_json(
            self, config_url_key: str, url_extra_path: str, json_data: dict) -> Tuple[
            requests.Response, dict]:
        """Post data to the specified url and get the result in json format.

        Args:
            config_url_key (str): key for the url in the config file
            url_extra_path (str): extra path to add to the url

        Returns:
            dict: [description]
        """
        response = self.post_json(config_url_key, url_extra_path, json_data)
        return response, response.json()


class CliOsduConnection(OsduConnection):
    """Specific class for use from the CLI that provides common error handling and messaging

    Args:
        OsduConnection ([type]): [description]
    """
    def cli_get_as_json(self, config_url_key: str, url_extra_path: str) -> dict:
        """[summary]

        Args:
            timeout (int, optional): [description]. Defaults to 60.
        """
        try:
            response, resp_json = self.get_as_json(config_url_key, url_extra_path)
            if response.status_code in [200]:
                return resp_json

            logger.error(MSG_HTTP_ERROR)
            logger.error("Error (%s) - %s", response.status_code, response.reason)
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.debug(ex)

        sys.exit(1)

    def cli_post_json_returning_json(self, config_url_key: str, url_extra_path: str, json_data: dict):
        """[summary]

        Args:
            config_url_key (str): [description]
            url_extra_path (str): [description]
            request_data (str): [description]

        Returns:
            [type]: [description]
        """
        try:
            response, resp_json = self.post_json_returning_json(config_url_key, url_extra_path, json_data)
            if response.status_code in [200]:
                return resp_json

            logger.error(MSG_HTTP_ERROR)
            logger.error("Error (%s) - %s", response.status_code, response.reason)
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
