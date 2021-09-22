# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for unit commands"""

import logging

from knack.testsdk import ScenarioTest
from mock import MagicMock, patch
from osdu.identity import OsduTokenCredential
from testfixtures import LogCapture

from osducli.click_cli import State
from osducli.cliclient import CliOsduClient
from osducli.commands.unit.list import unit_list
from osducli.config import CONFIG_AUTHENTICATION_MODE, CONFIG_SERVER


def mock_config_values(section, name, fallback=None):  # pylint: disable=W0613
    """Validate and mock config returns"""
    # if section != 'core':
    #     raise ValueError(f'Cannot retrieve config section \'{section}\'')
    if name == CONFIG_SERVER:
        return "https://dummy.com"
    if name == CONFIG_AUTHENTICATION_MODE:
        return "refresh_token"
    return f"{section}_{name}"


MOCK_CONFIG = MagicMock()
MOCK_CONFIG.get.side_effect = mock_config_values


class UnitTests(ScenarioTest):
    """Test cases for unit commands

    Uses the VCR library to record / replay HTTP requests into
    a file.
    """

    def __init__(self, method_name):
        super().__init__(None, method_name, filter_headers=["Authorization"])
        self.recording_processors = [self.name_replacer]
        self.vcr.register_matcher("always", UnitTests._vcrpy_match_always)
        self.vcr.match_on = ["always"]

    # If doing a new live test to get / refresh a recording then:
    # - Comment out the below patch and remove the get_headers parameter
    # - After getting a recording, delete any recording authentication interactions
    # - Delete or obfuscate any other sensitive information.
    # - Adjust test case as necessary e.g. totalCount
    # - Add patch and parameter back
    @patch.object(OsduTokenCredential, "get_token", return_value="DUMMY_ACCESS_TOKEN")
    def test_unit_list(self, get_headers):  # pylint: disable=W0613
        """Test for a successful response"""

        self.cassette.filter_headers = ["Authorization"]
        state = State()
        state.config = MOCK_CONFIG

        with LogCapture(level=logging.WARN) as log_capture:
            result = unit_list(state)
            assert isinstance(result, dict)
            assert result["totalCount"] == 3695
            assert result["count"] == 3
            assert len(result["units"]) == result["count"]
            assert len(log_capture.records) == 0

    @patch.object(CliOsduClient, "cli_get_returning_json", side_effect=SystemExit(1))
    def test_unit_list_exit(self, mock_cli_get_returning_json):  # pylint: disable=W0613
        """Test any exit error is propogated"""
        state = State()
        state.config = MOCK_CONFIG

        with self.assertRaises(SystemExit) as sysexit:
            _ = unit_list(state)
            self.assertEqual(sysexit.exception.code, 1)

    @classmethod
    def _vcrpy_match_always(cls, url1, url2):  # pylint: disable=W0613
        """Return true always (only 1 query)."""
        return True


if __name__ == "__main__":
    import nose2

    nose2.main()
