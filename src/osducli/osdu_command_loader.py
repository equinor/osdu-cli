# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Command and help loader for the OSDU CLI.

Commands are stored as one to one mappings between command line syntax and
python function.
"""

from collections import OrderedDict
import json
from knack.arguments import ArgumentsContext, CLIArgumentType
from knack.commands import CLICommandsLoader, CommandGroup

EXCLUDED_PARAMS = ['self', 'raw', 'custom_headers', 'operation_config',
                   'content_version', 'kwargs', 'client']


def dont_order_columns_table_transformer(rows):
    """Dummy function to stop knack ordering table columns in alphabetical order.

    Args:
        rows ([type]): [description]

    Returns:
        [type]: [description]
    """
    return rows


def unit_list_table_transformer(unit_list_json):
    """Transform unit list json to table.

    Args:
        json ([type]): [description]

    Returns:
        [type]: [description]
    """
    rows = [OrderedDict([('DisplaySymbol', record['displaySymbol']),
                         ('Name', record['name']),
                         ('Source', record['source'])])
            for record in unit_list_json['units']]

    return rows


class OsduCommandLoader(CLICommandsLoader):
    """OSDU CLI command loader, containing command mappings"""

    def __init__(self, *args, **kwargs):
        super(OsduCommandLoader, self).__init__(
            *args,
            excluded_command_handler_args=EXCLUDED_PARAMS,
            **kwargs)

    def load_command_table(self, args):  # pylint: disable=too-many-statements
        """Load all OSDU commands"""

        with CommandGroup(self, 'dataload', self.command_group_module('dataload')) as group:
            group.command('ingest', 'ingest')
            group.command('listworkflows', 'list_workflows')
            group.command('status', 'status')
            group.command('verify', 'verify')

        with CommandGroup(self, 'config', self.command_group_module('config')) as group:
            group.command('update', 'update')
            group.command('set-default', 'set_default')

        with CommandGroup(self, 'list', self.command_group_module('list')) as group:
            group.command('records', 'records', table_transformer=dont_order_columns_table_transformer)

        with CommandGroup(self, '', 'osducli.commands.status.custom#status') as group:
            group.command('status', 'status', table_transformer=dont_order_columns_table_transformer)

        with CommandGroup(self, 'unit', self.command_group_module('unit')) as group:
            group.command('list', 'unit_list', table_transformer=unit_list_table_transformer)

        with CommandGroup(self, '', self.command_group_module('version')) as group:
            group.command('version', 'version')

        return OrderedDict(self.command_table)

    def load_arguments(self, command):
        """Load specialized arguments for commands"""

        with ArgumentsContext(self, '') as arg_context:  # Global argument
            arg_context.argument('timeout', type=int, options_list=('-t', '--timeout'))

        with ArgumentsContext(self, 'dataload ingest') as arg_context:
            arg_context.argument('path', type=str, options_list=('-p', '--path'),
                                 help='Path to a file or folder containing manifests to upload.')
            arg_context.argument('files', type=str, options_list=('-f', '--files'),
                                 help='Associated files to upload for Work-Products.')
            arg_context.argument('batch_size', type=str, options_list=('-b', '--batch'),
                                 help='Batch size')
            arg_context.argument('runid_log', type=str, options_list=('-rl', '--runid-log'),
                                 help='Path of file to record returned run ids')

        with ArgumentsContext(self, 'dataload status') as arg_context:
            arg_context.argument('runid', type=str, options_list=('-r', '--runid'),
                                 help='Runid to query status of.', required=False)
            arg_context.argument('runid_log', type=str, options_list=('-rl', '--runid-log'),
                                 help='Path to a file containing run ids to get status of (see dataload ingest -h).')
            arg_context.argument('wait', action='store_true', options_list=('--wait', '-w'),
                                 help='Whether to wait for runs to complete')

        with ArgumentsContext(self, 'dataload verify') as arg_context:
            arg_context.argument('path', type=str, options_list=('-p', '--path'),
                                 help='Path to a file containing run ids to get status of (see dataload ingest -h).')
            arg_context.argument('batch_size', type=str, options_list=('-b', '--batch'),
                                 help='Batch size')

        # When the options_list is provided either for this timeout or the global timeout, the text
        # in the help file is ignored, so we are putting the help text here instead.
        with ArgumentsContext(self, 'list upgrade') as arg_context:
            arg_context.argument('timeout', type=int, options_list=('-t', '--timeout'),
                                 help='The total timeout in seconds. '
                                      'Upload will fail and return error after the upload timeout '
                                      'duration has passed. This timeout applies to '
                                      'the entire application package, and individual file timeouts '
                                      'will equal the remaining timeout duration. '
                                      'Timeout does not include the time required to '
                                      'compress the application package. ')

        with ArgumentsContext(self, 'list upgrade-update') as arg_context:
            arg_context.argument('parameters', type=self.json_encoded)
            arg_context.argument('metrics', type=self.json_encoded)
            arg_context.argument('min_node_count', type=int)
            arg_context.argument('max_node_count', type=int)

        with ArgumentsContext(self, 'is') as arg_context:
            # expect the parameter command_input in the python method as --command in commandline.
            arg_context.argument('command_input',
                                 CLIArgumentType(options_list='--command'))

        super(OsduCommandLoader, self).load_arguments(command)

    @staticmethod
    def command_group_module(name):
        """Return the name of the command module"""
        return 'osducli.commands.{}.custom#{{}}'.format(name)

    @staticmethod
    def json_encoded(arg_str):
        """Convert from argument JSON string to complex object.
        This function also accepts a file path to a .txt file containing the JSON string.
        File paths should be prefixed by '@'
        Path can be relative path or absolute path."""

        if arg_str and arg_str[0] == '@':
            try:
                with open(arg_str[1:], 'r') as json_file:
                    json_str = json_file.read()
                    return json.loads(json_str)
            except IOError:
                # This is the error that python 2.7 returns on no file found
                print('File not found at {0}'.format(arg_str[1:]))
            except ValueError as ex:
                print('Decoding JSON value from file {0} failed: \n{1}'.format(arg_str[1:], ex))
                raise

        try:
            return json.loads(arg_str)
        except ValueError as ex:
            print('Loading JSON from string input failed. '
                  'You can also pass the json argument in a .txt file. \n'
                  'To do so, set argument value to the absolute path of the text file '
                  'prefixed by "@". \nIf you have passed in a file name, please ensure that the JSON '
                  'is correct. Error: \n{0}'.format(ex))
            raise
