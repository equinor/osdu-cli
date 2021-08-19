# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""
from collections import OrderedDict
import json
from osducli.connection import OsduConnection


def records():
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    request_data = {
        "kind": "*:*:*:*",
        "limit": 1,
        "query": "*",
        "aggregateBy": "kind"
    }

    connection = OsduConnection()
    _, json_response = connection.post_as_json('search_url', 'query', json.dumps(request_data))

    services = [OrderedDict([('Kind', record['key']), ('Count', record['count'])])
                for record in json_response['aggregations']]
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
