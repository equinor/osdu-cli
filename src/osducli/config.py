# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Read and modify configuration settings related to the CLI"""

import os
import json
from six.moves import configparser  # pylint: disable=redefined-builtin
from knack.config import CLIConfig, _UNSET
from adal.token_cache import TokenCache

# Default names
SF_CLI_NAME = 'osducli'
SF_CLI_CONFIG_DIR = os.path.expanduser(os.path.join('~', '.{0}'.format(SF_CLI_NAME)))
SF_CLI_ENV_VAR_PREFIX = SF_CLI_NAME

CONFIG_SERVER = 'server'
CONFIG_FILE_URL = 'file-url'
CONFIG_SCHEMA_URL = 'schema-url'
CONFIG_SEARCH_URL = 'search-url'
CONFIG_STORAGE_URL = 'storage-url'
CONFIG_UNIT_URL = 'unit-url'
CONFIG_WORKFLOW_URL = 'workflow-url'

CONFIG_DATA_PARTITION_ID = 'data-partition-id'
CONFIG_LEGAL_TAG = 'legal-tag'
CONFIG_ACL_VIEWER = 'acl-viewer'
CONFIG_ACL_OWNER = 'acl-owner'

CONFIG_AUTHENTICATION_MODE = 'authentication-mode'

CONFIG_AUTHENTICATION_AUTHORITY = 'authority'
CONFIG_AUTHENTICATION_SCOPES = 'scopes'

CONFIG_TOKEN_ENDPOINT = 'token-endpoint'
CONFIG_REFRESH_TOKEN = 'refresh-token'
CONFIG_CLIENT_ID = 'client-id'
CONFIG_CLIENT_SECRET = 'client-secret'


def get_config_value(name, section=SF_CLI_NAME, fallback=_UNSET):
    """Gets a config by name.

    In the case where the config name is not found, will use fallback value."""

    cli_config = CLIConfig(SF_CLI_CONFIG_DIR, SF_CLI_ENV_VAR_PREFIX)

    return cli_config.get(section, name, fallback)


def get_config_bool(name, section=SF_CLI_NAME, fallback=_UNSET):
    """Checks if a config value is set to a valid bool value."""

    cli_config = CLIConfig(SF_CLI_CONFIG_DIR, SF_CLI_ENV_VAR_PREFIX)
    return cli_config.getboolean(section, name, fallback)


def get_config_int(name, section=SF_CLI_NAME, fallback=_UNSET):
    """Checks if a config value is set to a valid int value."""

    cli_config = CLIConfig(SF_CLI_CONFIG_DIR, SF_CLI_ENV_VAR_PREFIX)
    return cli_config.getint(section, name, fallback)


def set_config_value(name, value, section=SF_CLI_NAME):
    """Set a config by name to a value."""

    cli_config = CLIConfig(SF_CLI_CONFIG_DIR, SF_CLI_ENV_VAR_PREFIX)
    cli_config.set_value(section, name, value)


def get_default_from_config(config, section, option, fallback=1):
    """Get the default value from configuration, replacing with fallback if not found"""
    try:
        return config.get(section, option)
    except (IndexError, configparser.NoSectionError, configparser.NoOptionError):
        return fallback


def get_default_choice_index_from_config(config, section, option, choice_list, fallback=1):
    """Get index + 1 of the current choice value from cong, replacing with fallback if not found"""
    try:
        config_val = config.get(section, option)
        return [i for i, x in enumerate(choice_list)
                if 'name' in x and x['name'] == config_val][0] + 1
    except (IndexError, configparser.NoSectionError, configparser.NoOptionError):
        return fallback


def client_endpoint():
    """Cluster HTTP gateway endpoint address and port, represented as a URL."""

    return get_config_value('endpoint', None)


def security_type():
    """The selected security type of client."""

    return get_config_value('security', None)


def set_cluster_endpoint(endpoint):
    """Configure cluster endpoint"""
    set_config_value('endpoint', endpoint)


def no_verify_setting():
    """True to skip certificate SSL validation and verification"""

    return get_config_bool('no_verify')


def set_no_verify(no_verify):
    """Configure if cert verification should be skipped."""
    if no_verify:
        set_config_value('no_verify', 'true')
    else:
        set_config_value('no_verify', 'false')


def ca_cert_info():
    """CA certificate(s) path"""

    if get_config_bool('use_ca'):
        return get_config_value('ca_path', fallback=None)
    return None


def set_ca_cert(ca_path=None):
    """Configure paths to CA cert(s)."""
    if ca_path:
        set_config_value('ca_path', ca_path)
        set_config_value('use_ca', 'true')
    else:
        set_config_value('use_ca', 'false')


def cert_info():
    """Path to certificate related files, either a single file path or a
    tuple. In the case of no security, returns None."""

    sec_type = security_type()
    if sec_type == 'pem':
        return get_config_value('pem_path', fallback=None)
    if sec_type == 'cert':
        cert_path = get_config_value('cert_path', fallback=None)
        key_path = get_config_value('key_path', fallback=None)
        return cert_path, key_path

    return None


def aad_cache():
    """AAD token cache."""
    token_cache = TokenCache()
    token_cache.deserialize(get_config_value('aad_cache', fallback=None))
    return json.loads(get_config_value('aad_token', fallback=None)), token_cache


def set_aad_cache(token, cache):
    """
    Set AAD token cache.
    :param token: dict with several keys, include "accessToken" and "refreshToken"
    :param cache: adal.token_cache.TokenCache
    :return: None
    """

    set_config_value('aad_token', json.dumps(token))
    set_config_value('aad_cache', cache.serialize())


def aad_metadata():
    """AAD metadata."""
    return get_config_value('authority_uri', fallback=None), \
        get_config_value('aad_resource', fallback=None), \
        get_config_value('aad_client', fallback=None)


def set_aad_metadata(uri, resource, client):
    """Set AAD metadata."""
    set_config_value('authority_uri', uri)
    set_config_value('aad_resource', resource)
    set_config_value('aad_client', client)


def set_auth(pem=None, cert=None, key=None, aad=False):
    """Set certificate usage paths"""

    if any([cert, key]) and pem:
        raise ValueError('Cannot specify both pem and cert or key')

    if any([cert, key]) and not all([cert, key]):
        raise ValueError('Must specify both cert and key')

    if pem:
        set_config_value('security', 'pem')
        set_config_value('pem_path', pem)
    elif cert or key:
        set_config_value('security', 'cert')
        set_config_value('cert_path', cert)
        set_config_value('key_path', key)
    elif aad:
        set_config_value('security', 'aad')
    else:
        set_config_value('security', 'none')


def using_aad():
    """
    :return: True if security type is 'aad'. False otherwise
    """
    return security_type() == 'aad'


def get_cluster_auth():
    """
    Return the information that was added to config file by the function select cluster.

    :return: a dictionary with keys: endpoint, cert, key, pem, ca, aad, no_verify
    """

    cluster_auth = dict()
    cluster_auth['endpoint'] = client_endpoint()
    cluster_auth['cert'] = get_config_value('cert_path')
    cluster_auth['key'] = get_config_value('key_path')
    cluster_auth['pem'] = get_config_value('pem_path')
    cluster_auth['ca'] = ca_cert_info()
    cluster_auth['aad'] = using_aad()
    cluster_auth['no_verify'] = no_verify_setting()

    return cluster_auth
