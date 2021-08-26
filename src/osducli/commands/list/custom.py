# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""
from collections import OrderedDict
from osducli.cliclient import CliOsduClient
from osducli.config import CONFIG_SEARCH_URL


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

    connection = CliOsduClient()
    json_response = connection.cli_post_returning_json(CONFIG_SEARCH_URL, 'query', request_data)

    services = [OrderedDict([('Kind', record['key']), ('Count', record['count'])])
                for record in json_response['aggregations']]
    return services
