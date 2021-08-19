# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for unit commands"""

import logging
from mock import patch
from knack.testsdk import ScenarioTest
from testfixtures import LogCapture
from osducli.commands.unit.custom import unit_list
from osducli.connection import CliOsduConnection


class UnitTests(ScenarioTest):
    """Test cases for unit commands

    Uses the VCR library to record / replay HTTP requests into
    a file.
    """

    def __init__(self, method_name):
        super(UnitTests, self).__init__(None, method_name)
        self.recording_processors = [self.name_replacer]

    def test_unit_list(self):
        """Test for a successful response"""
        with LogCapture(level=logging.WARN) as log_capture:
            result = unit_list()
            assert isinstance(result, dict)
            assert result['totalCount'] == 3695
            assert len(log_capture.records) == 0

    @patch.object(CliOsduConnection, 'cli_get_as_json', side_effect=SystemExit(1))
    def test_unit_list_exit(self, mock_cli_get_as_json):
        """Test any exit error is propogated"""
        with self.assertRaises(SystemExit) as sysexit:
            _ = unit_list()
            self.assertEqual(sysexit.exception.code, 1)


if __name__ == '__main__':
    import nose2
    nose2.main()
