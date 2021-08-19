# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Useful functions."""

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

from osducli.config import get_config_int, get_config_value

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
    def __init__(self, *args, **keywords):
        # self.__config = config
        self.__args = args          # pylint: disable=W0238
        self.__keywords = keywords  # pylint: disable=W0238
        self.__expire_date = 0
        self._id_token = None
        self._access_token = None

        try:
            self._retries = get_config_int("retries", "core", 2)
            self._token_endpoint = get_config_value("token_endpoint", "core")
            self._refresh_token = get_config_value("REFRESH_TOKEN", "core")
            self._client_id = get_config_value("CLIENT_ID", "core")
            self._client_secret = get_config_value("CLIENT_SECRET", "core")
        except (NoOptionError, NoSectionError) as ex:
            logger.warning("'%s' missing from configuration. Run osducli configure", ex.args[0])
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

    def refresh(self):
        """
        Refresh token and save them into class.
        """
        logger.info("Refreshing token.")

        for i in range(self._retries):
            # try several times if there any error
            try:
                resp = self.refresh_request(
                    self._token_endpoint, self._refresh_token, self._client_id, self._client_secret)
            except HTTPError:
                if i == self._retries - 1:
                    # too many errors, raise original exception
                    raise
        self._id_token = resp["id_token"]
        self._access_token = resp["access_token"]
        self.__expire_date = datetime.now().timestamp() + resp["expires_in"]

        logger.info("Token is refreshed.")

    @staticmethod
    def refresh_request(url: str, refresh_token: str, client_id: str, client_secret: str) -> dict:
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

    def get_token(self) -> str:
        """
        Refresh access or id token depending on config settings.

        :param RawConfigParser config: config that is used in calling module
        :return: token of requested type
        :rtype: str
        """
        token_type = get_config_value("token_type", "core")

        tokens_dict = {
            "access_token": self.access_token(),
            "id_token": self.id_token()
        }

        if token_type not in tokens_dict.keys():
            logger.error("Unknown type of token %s. Set correct token type in config file.", token_type)
            sys.exit(2)

        return tokens_dict.get(token_type)

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
            "data-partition-id": get_config_value("data-partition-id", "core"),
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
        server = get_config_value('server', 'core')
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

    def post(self, config_url_key: str, url_extra_path: str, data: str) -> requests.Response:
        """Post data to a url

        Args:
            config_url_key (str): key for the url in the config file
            url_extra_path (str): extra path to add to the url

        Returns:
            requests.Response: [description]
        """
        server = get_config_value('server', 'core')
        unit_url = get_config_value(config_url_key, 'core')
        url = urljoin(server, unit_url) + url_extra_path

        headers = self.get_headers()
        response = requests.post(url, data, headers=headers)
        return response

    def post_as_json(self, config_url_key: str, url_extra_path: str, data: str) -> Tuple[requests.Response, dict]:
        """Post data to the specified url and get the result in json format.

        Args:
            config_url_key (str): key for the url in the config file
            url_extra_path (str): extra path to add to the url

        Returns:
            dict: [description]
        """
        response = self.post(config_url_key, url_extra_path, data)
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
            response, json = self.get_as_json(config_url_key, url_extra_path)
            if response.status_code in [200]:
                return json

            logger.error(MSG_HTTP_ERROR)
            logger.error("Error (%s) - %s", response.status_code, response.reason)
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.debug(ex)

        sys.exit(1)
