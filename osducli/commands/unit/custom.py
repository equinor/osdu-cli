# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""
from collections import OrderedDict
from urllib.parse import urljoin
import requests
from osducli.connection import get_headers
from osducli.config import get_config_value


def list():
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    headers = get_headers()

    server = get_config_value('server', 'core')
    search_url = get_config_value('unit_url', 'core')
    url = urljoin(server, search_url) + 'unit?limit=10000'
    response = requests.get(url,
                            headers=headers)

    search_response = response.json()
    # print(json.dumps(search_response, indent=2))

    services = [OrderedDict([('DisplaySymbol', record['displaySymbol']), ('Name', record['name'])])
                for record in search_response['units']]
    return services
