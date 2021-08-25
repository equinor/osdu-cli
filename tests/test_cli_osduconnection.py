# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Test cases for CliOsduClient"""

import logging

from mock import MagicMock, PropertyMock, patch
from knack.testsdk import ScenarioTest
from testfixtures import LogCapture

from osdu.identity import OsduTokenCredential

from osducli.cliclient import CliOsduClient
from osducli.cliclient import MSG_HTTP_ERROR
from osducli.config import CONFIG_SERVER, CONFIG_AUTHENTICATION_MODE


def mock_config_values(section, name, fallback=None):  # pylint: disable=W0613
    """Validate and mock config returns"""
    # if section != 'core':
    #     raise ValueError(f'Cannot retrieve config section \'{section}\'')
    if name == CONFIG_SERVER:
        return 'https://dummy.com'
    if name == CONFIG_AUTHENTICATION_MODE:
        return 'refresh_token'
    return f'{section}_{name}'


MOCK_CONFIG = MagicMock()
MOCK_CONFIG.return_value.get.side_effect = mock_config_values


class CliOsduClientTests(ScenarioTest):
    """Test cases for unit commands

    Uses the VCR library to record / replay HTTP requests into
    a file.
    """

    # @staticmethod
    # def is_json(myjson):
    #     try:
    #         _ = json.loads(myjson)
    #     except ValueError:
    #         return False
    #     return True

    def __init__(self, method_name):
        super().__init__(None, method_name, filter_headers=['Authorization'])
        self.recording_processors = [self.name_replacer]
        self.vcr.register_matcher('always', CliOsduClientTests._vcrpy_match_always)
        self.vcr.match_on = ['always']

    # """Playground test for unit commands - some notes / examples"""
    # @patch('osducli.commands.unit.custom.get_as_json', side_effect=ValueError('ValueError'))
    # @patch('osducli.commands.unit.custom.get_url_as_json', autospec=True, return_value=(not_found_response_mock,None))
    #
    # @patch('osducli.commands.unit.custom.get_headers')
    # def test_unit_list(self, test_patch):

    #     # with patch('app.mocking.get_user_name', return_value = 'Mocked This Silly'):
    #     #     ret = test_method()
    #     #     self.assertEqual(ret, 'Mocked This Silly')

    #     unit_list()

    # If doing a new live test to get / refresh a recording then comment out the below patch and
    # after getting a recording delete any recording authentication interactions
    # @patch.object(CliOsduClient, 'get_headers', return_value={})
    @patch.object(OsduTokenCredential, 'get_token', return_value='DUMMY_ACCESS_TOKEN')
    @patch('osducli.config.CLIConfig', new=MOCK_CONFIG)
    def test_cli_osdu_connection_cli_get_as_json(self, mock_get_headers):  # pylint: disable=W0613
        """Test valid response returns correct json"""

        self.cassette.filter_headers = ['Authorization']

        with LogCapture(level=logging.WARN) as log_capture:
            connection = CliOsduClient()
            result = connection.cli_get_returning_json('unit_url', 'unit?limit=3')
            assert isinstance(result, dict)
            assert result['count'] == 3
            self.assertEqual(len(log_capture.records), 0)

    not_found_response_mock = MagicMock()
    type(not_found_response_mock).status_code = PropertyMock(return_value=404)
    not_found_response_mock.reason = "Not Found"

    # pylint: disable=W0613
    @patch.object(CliOsduClient, '_url_from_config', return_value='https://www.test.com/test')
    @patch.object(CliOsduClient, 'get', return_value=not_found_response_mock)
    def test_cli_osdu_connection_cli_get_returning_json_404(self, mock_url_from_config, mock_get):
        """Test 404 errors return the correct message"""
        with self.assertRaises(SystemExit) as sysexit:
            with LogCapture(level=logging.INFO) as log_capture:
                connection = CliOsduClient()
                _ = connection.cli_get_returning_json('DUMMY_KEY', 'DUMMY_STRING')
                log_capture.check_present(
                    ('cli', 'ERROR', MSG_HTTP_ERROR)
                )
            self.assertEqual(sysexit.exception.code, 1)

    # # pylint: disable=W0613
    # @patch.object(CliOsduClient, '_url_from_config', return_value='https://www.test.com/test')
    # @patch.object(Response, 'json', return_value='BAD JSON')
    # @patch.object(CliOsduClient, 'cli_get_returning_json', side_effect=ValueError('ValueError'))
    # def test_cli_osdu_connection_get_as_json_bad_json(self):  #, mock_url_from_config, mock_cli_get_returning_json):
    #     """Test json decode error returns the correct message"""
    #     with self.assertRaises(SystemExit) as sysexit:
    #         with LogCapture(level=logging.INFO) as log_capture:
    #             connection = CliOsduClient()
    #             _ = connection.cli_get_returning_json('DUMMY_URL', 'DUMMY_STRING')
    #             log_capture.check(
    #                 ('cli', 'ERROR', MSG_JSON_DECODE_ERROR)
    #             )
    #         self.assertEqual(sysexit.exception.code, 1)

    @classmethod
    def _vcrpy_match_always(cls, url1, url2):  # pylint: disable=W0613
        """ Return true always (only 1 query). """
        return True


if __name__ == '__main__':
    import nose2
    nose2.main()
