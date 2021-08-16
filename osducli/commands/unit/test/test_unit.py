
import json
import logging
from mock import MagicMock, PropertyMock, patch
from knack.testsdk import ScenarioTest
from testfixtures import LogCapture
from osducli.commands.unit.consts import MSG_JSON_DECODE_ERROR, MSG_HTTP_ERROR
from osducli.commands.unit.custom import unit_list


def mock_config_values(section, name, fallback):
    """Validate and mock config returns"""
    if section != 'core':
        raise ValueError(f'Cannot retrieve config section \'{section}\'')
    if name == 'server':
        return 'http://www.www.com/'
    if name == 'unit_url':
        return '/unit/'
    return fallback


MOCK_CONFIG = MagicMock()
MOCK_CONFIG.return_value.get.side_effect = mock_config_values


class UnitTests(ScenarioTest):
    """Playground test for unit commands"""

    """HTTP request generation tests for Service Fabric commands.
    This class requires a live connection to a cluster for some tests.
    This is so we generate commands in the way that the users will.
    The purpose of this test is to generate the commands and
    read the HTTP request to ensure correctness. The expected values are hard-coded.
    The VCR library records all HTTP requests into
    a file. For the sake of clarity, each test writes to its own file.
    The tests should then read the file to validate correctness. For on the fly debugging,
    printing to stdout does not print to the terminal/command line.
    Please use other outputs, such as stderr."""

    @staticmethod
    def is_json(myjson):
        try:
            _ = json.loads(myjson)
        except ValueError:
            return False
        return True

    def __init__(self, method_name):
        super(UnitTests, self).__init__(None, method_name)
        self.recording_processors = [self.name_replacer]

    # """Playground test for unit commands"""
    # @patch('osducli.commands.unit.custom.get_headers')
    # @patch('osducli.config.CLIConfig', new=MOCK_CONFIG)
    # def test_unit_list(self, test_patch):

    #     # with patch('app.mocking.get_user_name', return_value = 'Mocked This Silly'):
    #     #     ret = test_method()
    #     #     self.assertEqual(ret, 'Mocked This Silly')

    #     unit_list()

    def test_unit_list(self):
        with LogCapture(level=logging.WARN) as log_capture:
            result = unit_list()
            assert isinstance(result, dict)
            assert result['totalCount'] == 3695
            assert len(log_capture.records) == 0

    not_found_response_mock = MagicMock()
    type(not_found_response_mock).status_code = PropertyMock(return_value=404)
    not_found_response_mock.reason = "Not Found"

    @patch('osducli.commands.unit.custom.get_url_as_json', autospec=True, return_value=(not_found_response_mock, None))
    def test_unit_list_404(self, mock_get_url_as_json):
        with LogCapture(level=logging.INFO) as log_capture:
            result = unit_list()
            assert result is None
            log_capture.check_present(
                ('cli', 'ERROR', MSG_HTTP_ERROR)
            )

    """Test json decode error returns the correct message"""
    @patch('osducli.commands.unit.custom.get_url_as_json', side_effect=ValueError('ValueError'))
    def test_unit_list_bad_json(self, mock_get_url_as_json):
        with LogCapture(level=logging.INFO) as log_capture:
            result = unit_list()
            assert result is None
            log_capture.check(
                ('cli', 'ERROR', MSG_JSON_DECODE_ERROR)
            )


if __name__ == '__main__':
    import nose2
    nose2.main()
