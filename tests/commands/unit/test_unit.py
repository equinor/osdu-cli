# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for unit commands"""

import logging
from mock import MagicMock, patch
from knack.testsdk import ScenarioTest
from testfixtures import LogCapture
from osducli.commands.unit.custom import unit_list
from osducli.connection import CliOsduConnection


def mock_config_values(section, name, fallback=None):  # pylint: disable=W0613
    """Validate and mock config returns"""
    # if section != 'core':
    #     raise ValueError(f'Cannot retrieve config section \'{section}\'')
    if name == 'server':
        return 'https://dummy.com'
    return f'{section}_{name}'


MOCK_CONFIG = MagicMock()
MOCK_CONFIG.return_value.get.side_effect = mock_config_values


class UnitTests(ScenarioTest):
    """Test cases for unit commands

    Uses the VCR library to record / replay HTTP requests into
    a file.
    """

    def __init__(self, method_name):
        super().__init__(None, method_name, filter_headers=['Authorization'])
        self.recording_processors = [self.name_replacer]
        self.vcr.register_matcher('always', UnitTests._vcrpy_match_always)
        self.vcr.match_on = ['always']

    # If doing a new live test to get / refresh a recording then:
    # - Comment out the below patch and remove the get_headers parameter
    # - After getting a recording, delete any recording authentication interactions
    # - Delete or obfuscate any other sensitive information.
    # - Adjust test case as necessary e.g. totalCount
    # - Add patch and parameter back
    @patch.object(CliOsduConnection, 'get_headers', return_value={})
    @patch('osducli.config.CLIConfig', new=MOCK_CONFIG)
    def test_unit_list(self, get_headers):  # pylint: disable=W0613
        """Test for a successful response"""

        self.cassette.filter_headers = ['Authorization']

        with LogCapture(level=logging.WARN) as log_capture:
            result = unit_list()
            assert isinstance(result, dict)
            assert result['totalCount'] == 3695
            assert result['count'] == 3
            assert len(result['units']) == result['count']
            assert len(log_capture.records) == 0

    @patch.object(CliOsduConnection, 'cli_get_returning_json', side_effect=SystemExit(1))
    def test_unit_list_exit(self, mock_cli_get_returning_json):  # pylint: disable=W0613
        """Test any exit error is propogated"""
        with self.assertRaises(SystemExit) as sysexit:
            _ = unit_list()
            self.assertEqual(sysexit.exception.code, 1)

    @classmethod
    def _vcrpy_match_always(cls, url1, url2):  # pylint: disable=W0613
        """ Return true always (only 1 query). """
        return True


if __name__ == '__main__':
    import nose2
    nose2.main()
