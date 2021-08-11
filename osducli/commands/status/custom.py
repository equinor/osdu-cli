# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Code to handle status commands"""

from collections import OrderedDict
from urllib.parse import urljoin
import requests
from osducli.connection import get_headers
from osducli.config import get_config_value


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

    return services
