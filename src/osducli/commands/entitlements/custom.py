# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom cluster upgrade specific commands"""
from osdu.entitlements import EntitlementsClient
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


@handle_cli_exceptions
def list_my_groups():
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    connection = CliOsduClient()

    entitlements_client = EntitlementsClient(connection)
    json_response = entitlements_client.list_groups()
    print("NOTE: Only shows groups that you have access to - rename to 'osducli entitlements mygroups'?\n\n")
    # TO DO: Get members to support table output, but should perhaps usa formatter class.
    return json_response


@handle_cli_exceptions
def list_group_members(group):
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    connection = CliOsduClient()

    entitlements_client = EntitlementsClient(connection)
    json_response = entitlements_client.list_group_members(group)

    # TO DO: Get members to support table output, but should perhaps usa formatter class.
    return json_response


@handle_cli_exceptions
def add_group(name):
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    connection = CliOsduClient()

    entitlements_client = EntitlementsClient(connection)
    json_response = entitlements_client.add_group(name)

    return json_response


@handle_cli_exceptions
def delete_group(group):
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    connection = CliOsduClient()

    entitlements_client = EntitlementsClient(connection)
    entitlements_client.delete_group(group)


@handle_cli_exceptions
def add_member(member, group):
    """[summary]

    Args:
        timeout (int, optional): [description]. Defaults to 60.
    """
    connection = CliOsduClient()

    entitlements_client = EntitlementsClient(connection)
    json_response = entitlements_client.add_member_to_group(member, group)

    return json_response
