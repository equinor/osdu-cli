# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""

from knack.log import get_logger

from osducli.connection import get_url_as_json
from osducli.commands.unit.consts import MSG_JSON_DECODE_ERROR, MSG_HTTP_ERROR


def unit_list():
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    logger = get_logger()
    try:
        response, json = get_url_as_json('unit_url', 'unit?limit=10000')
        if response.status_code in [200]:
            return json
        else:
            logger.error(MSG_HTTP_ERROR)
            logger.error(f"Error ({response.status_code}) - {response.reason}")
            return None
    except ValueError as ex:
        logger.error(MSG_JSON_DECODE_ERROR)
        logger.debug(ex)
        return None
