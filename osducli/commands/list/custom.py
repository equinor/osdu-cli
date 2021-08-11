# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""
from collections import OrderedDict
import json
from urllib.parse import urljoin
import requests
from osducli.connection import get_headers
from osducli.config import get_config_value


def records():
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    headers = get_headers()
    request_data = {
        "kind": "*:*:*:*",
        "limit": 1,
        "query": "*",
        "aggregateBy": "kind"
    }

    server = get_config_value('server', 'core')
    search_url = get_config_value('search_url', 'core')
    url = urljoin(server, search_url) + 'query'
    response = requests.post(url,
                             json.dumps(request_data),
                             headers=headers)

    search_response = response.json()
    # print(json.dumps(search_response, indent=2))

    services = [OrderedDict([('Kind', record['key']), ('Count', record['count'])])
                for record in search_response['aggregations']]
    return services


def upgrade_update(min_node_count, max_node_count, timeout=60):
    """[summary]

    Args:
        min_node_count ([type]): [description]
        max_node_count ([type]): [description]
        timeout (int, optional): [description]. Defaults to 60.
    """
    print("NOT IMPLEMENTED - DUMMY CODE / NOT VALID CALL")
    print(f"Upgrade:min_node_count {min_node_count}, max_node_count {max_node_count}, timeout{timeout}")
