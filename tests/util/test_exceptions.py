# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Test cases for osducli.util.exceptions"""


import unittest

from nose2.tools import params

from osducli.util.exceptions import CliError

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-public-methods


class TestExceptions(unittest.TestCase):

    # pylint: disable=no-self-use
    @params("Test message", "Test message 2")
    def test_cli_error(self, message):
        try:
            raise CliError(message)
        except CliError as ex:
            self.assertEqual(message, ex.message)


if __name__ == "__main__":
    import nose2

    nose2.main()
