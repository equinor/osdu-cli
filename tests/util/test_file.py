# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Test cases for osducli.util.file"""


import os
import tempfile
from os import makedirs, path

from knack.testsdk.base import IntegrationTestBase
from nose2.tools import params

from osducli.util.file import ensure_directory_exists, get_files_from_path

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-public-methods


# pylint: disable=no-self-use
class TestExceptions(IntegrationTestBase):
    def __init__(self, method_name):
        super().__init__(None, method_name)

    # region ensure_directory_exists

    @params("dir1", "dir2")
    def test_ensure_directory_exists(self, directory):
        temp_dir = self.create_temp_dir()
        final_dir = path.join(temp_dir, directory)
        ensure_directory_exists(final_dir)

        self.assertTrue(path.isdir(final_dir))

    @params("dir1", "dir2")
    def test_ensure_directory_exists_already_exists(self, directory):
        temp_dir = self.create_temp_dir()
        final_dir = path.join(temp_dir, directory)
        makedirs(final_dir)
        ensure_directory_exists(final_dir)

    def test_ensure_directory_exists_file_not_dir(self):
        temp_file = self.create_temp_file(5)
        ensure_directory_exists(temp_file)

    def test_ensure_directory_exists_bad_path(self):
        with self.assertRaises(Exception) as _:
            ensure_directory_exists("\\\\\\\\XXXXX\\")

    # endregion

    # region get_files_from_path

    def test_get_files_from_path_file(self):
        temp_file = self.create_temp_file(5)

        files = get_files_from_path(temp_file)

        self.assertEqual(1, len(files))
        self.assertEqual(files[0], temp_file)

    def test_get_files_from_path_dir(self):
        temp_dir = self.create_temp_dir()
        _fd, file1 = tempfile.mkstemp(dir=temp_dir)
        os.close(_fd)
        _fd, file2 = tempfile.mkstemp(dir=temp_dir)
        os.close(_fd)

        files = get_files_from_path(temp_dir)

        self.assertEqual(2, len(files))
        self.assertTrue(file1 in files)
        self.assertTrue(file2 in files)

    def test_get_files_from_path_dir_nested(self):
        temp_dir = self.create_temp_dir()
        sub_dir = tempfile.mkdtemp(dir=temp_dir)
        _fd, file1 = tempfile.mkstemp(dir=sub_dir)
        os.close(_fd)

        files = get_files_from_path(temp_dir)

        self.assertEqual(1, len(files))
        self.assertTrue(file1 in files)

    # endregion


if __name__ == "__main__":
    import nose2

    nose2.main()
