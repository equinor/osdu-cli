# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom commands for the Service Fabric container support"""

import json


def invoke_api(  # pylint: disable=too-many-arguments
        timeout=60):
    """Invoke container API on a cluster node"""
    print(timeout)
    print("NOT IMPLEMENTED - DUMMY CODE / NOT VALID CALL")


def logs(  # pylint: disable=too-many-arguments
        timeout=60):
    """Get container logs"""
    print(timeout)
    print("NOT IMPLEMENTED - DUMMY CODE / NOT VALID CALL")


def format_response(response):
    """ pretty print json response """
    # Note: We are not printing the entire response type
    # (azure.servicefabric.models.container_api_response_py3.ContainerApiResponse), but instead,
    # printing only ContainerApiResult because it contains all the data, and we avoid the need
    # to use jsonpickle encoding
    if response and response.container_api_result:
        return json.dumps(response.container_api_result.__dict__, sort_keys=True, indent=4)
    return None
