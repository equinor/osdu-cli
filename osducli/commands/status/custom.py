# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Code to handle status commands"""

from collections import OrderedDict
from configparser import NoSectionError, NoOptionError
from urllib.parse import urljoin
import requests
from knack.log import get_logger
from osducli.connection import get_headers
from osducli.config import get_config_value

logger = get_logger(__name__)


def _get_status(server, api, path, headers):
    url = urljoin(server, api) + path
    response = requests.get(url, headers=headers)
    return response.status_code, response.reason


def status():
    """status command entry point

    Returns:
        [type]: [description]
    """
    headers = get_headers()

    services = []
    try:
        server = get_config_value('server', 'core')

        code, reason = _get_status(server, get_config_value('search_url', 'core'), 'health/readiness_check', headers)
        services.append(OrderedDict([('Service', 'Search service'), ('Code', code), ('Reason', reason)]))

        code, reason = _get_status(server, get_config_value('schema_url', 'core'), 'schema?limit=1', headers)
        services.append(OrderedDict([('Service', 'Schema service'), ('Code', code), ('Reason', reason)]))

        code, reason = _get_status(server, get_config_value('workflow_url', 'core'), 'readiness_check', headers)
        services.append(OrderedDict([('Service', 'Workflow service'), ('Code', code), ('Reason', reason)]))

        code, reason = _get_status(server, get_config_value('storage_url', 'core'), 'health', headers)
        services.append(OrderedDict([('Service', 'Storage service'), ('Code', code), ('Reason', reason)]))

        code, reason = _get_status(server, get_config_value('file_url', 'core'), 'readiness_check', headers)
        services.append(OrderedDict([('Service', 'File service'), ('Code', code), ('Reason', reason)]))

    except (IndexError, NoSectionError, NoOptionError) as ex:
        logger.error("'%s' missing from configuration. Run osducli configure or add manually", ex.args[0])

    return services
