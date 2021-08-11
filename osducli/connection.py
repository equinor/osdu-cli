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
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from knack.log import get_logger

from osducli.config import get_config_int, get_config_value

logger = get_logger(__name__)


#  pylint: disable=R0903
class ClassProperty:
    """
    Decorator that allows get methods like class properties.
    """

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


classproperty = ClassProperty  # pylint: disable=C0103


class TokenManager:
    """
    Class for token managing.

    Simple usage:
    print(TokenManager.id_token)
    print(TokenManager.access_token)

    Requires dataload.ini with:
    [core]
    token_endpoint = <token_endpoint_url>
    retries = <retries_count>

    Requires "REFRESH_TOKEN", "CLIENT_ID", "CLIENT_SECRET" in environment variables
    """
    expire_date = 0

    try:
        _retries = get_config_int("retries", "core", 2)
        _token_endpoint = get_config_value("token_endpoint", "core")
        _refresh_token = get_config_value("REFRESH_TOKEN", "core")
        _client_id = get_config_value("CLIENT_ID", "core")
        _client_secret = get_config_value("CLIENT_SECRET", "core")
    except (NoOptionError, NoSectionError):  # as ex:
        pass
        # logger.warn("'%s' missing from configuration. Run osducli configure", ex.args[0])
        # sys.exit(0)

    # @staticmethod
    # def _token_endpoint():  # pylint: disable=E0213
    #     """ Lazy load of token endpoint """
    #     try:
    #         return get_config_value("token_endpoint", "core")
    #     except (NoOptionError, NoSectionError) as ex:
    #         logger.error("'%s' missing from configuration. Run osducli configure", ex.args[0])
    #         sys.exit(0)

    # @staticmethod
    # def _refresh_token():  # pylint: disable=E0213
    #     """ Lazy load of refresh token """
    #     try:
    #         return get_config_value("REFRESH_TOKEN", "core")
    #     except (NoOptionError, NoSectionError) as ex:
    #         logger.error("'%s' missing from configuration. Run osducli configure", ex.args[0])
    #         sys.exit(0)

    # @staticmethod
    # def _client_id():  # pylint: disable=E0213
    #     """ Lazy load of client id """
    #     try:
    #         return get_config_value("CLIENT_ID", "core")
    #     except (NoOptionError, NoSectionError) as ex:
    #         logger.error("'%s' missing from configuration. Run osducli configure", ex.args[0])
    #         sys.exit(0)

    # @staticmethod
    # def _client_secret():  # pylint: disable=E0213
    #     """ Lazy load of client secret """
    #     try:
    #         return get_config_value("CLIENT_SECRET", "core")
    #     except (NoOptionError, NoSectionError) as ex:
    #         logger.error("'%s' missing from configuration. Run osducli configure", ex.args[0])
    #         sys.exit(0)

    @classproperty
    def id_token(cls):  # pylint: disable=E0213
        """
        Check expiration date and return id_token.
        """
        if datetime.now().timestamp() > cls.expire_date:
            cls.refresh()
        return cls._id_token

    @classproperty
    def access_token(cls):  # pylint: disable=E0213
        """
        Check expiration date and return access_token.
        """
        if datetime.now().timestamp() > cls.expire_date:
            cls.refresh()
        return cls._access_token

    @classmethod
    def refresh(cls):
        """
        Refresh token and save them into class.
        """
        logger.info("Refreshing token.")

        for i in range(cls._retries):
            # try several times if there any error
            try:
                resp = cls.refresh_request(
                    cls._token_endpoint, cls._refresh_token, cls._client_id, cls._client_secret)
            except HTTPError:
                if i == cls._retries - 1:
                    # too many errors, raise original exception
                    raise
        cls._id_token = resp["id_token"]
        cls._access_token = resp["access_token"]
        cls.expire_date = datetime.now().timestamp() + resp["expires_in"]

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


def get_token() -> str:
    """
    Refresh access or id token depending on config settings.

    :param RawConfigParser config: config that is used in calling module
    :return: token of requested type
    :rtype: str
    """
    token_type = get_config_value("token_type", "core")

    tokens_dict = {
        "access_token": TokenManager.access_token,
        "id_token": TokenManager.id_token
    }

    if token_type not in tokens_dict.keys():
        logger.error("Unknown type of token %s. Set correct token type in config file.", token_type)
        sys.exit(2)

    return tokens_dict.get(token_type)


def get_headers() -> dict:
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
        "Authorization": f"Bearer {get_token()}",
        "correlation-id": correlation_id
    }
