# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import errno
import os


def get_files_from_path(path: str) -> list:
    """Given a path get a list of all files.

    Args:
        path (str): path

    Returns:
        list: list of file paths
    """
    allfiles = []
    if os.path.isfile(path):
        allfiles = [path]

    # Recursive traversal of files and subdirectories of the root directory and files processing
    for root, _, files in os.walk(path):
        for file in files:
            allfiles.append(os.path.join(root, file))
    return allfiles


def ensure_directory_exists(directory: str):
    """Create a directory if it doesn't exist"""
    if not os.path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError as _e:
            if _e.errno != errno.EEXIST:
                raise _e
