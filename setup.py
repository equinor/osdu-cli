# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Azure Service Fabric CLI package that can be installed using setuptools"""

import os
import re
from setuptools import setup, find_packages


def read(fname):
    """Local read helper function for long documentation"""
    osducli_path = os.path.dirname(os.path.realpath(__file__))
    return open(os.path.join(osducli_path, fname)).read()


version_file = read(os.path.join('osducli', '__init__.py'))
__VERSION__ = re.search(r'^__VERSION__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        version_file, re.MULTILINE).group(1)

setup(
    name='osducli',
    version=__VERSION__,
    description='OSDU command line',
    long_description=read('README.rst'),
    url='https://github.com/equinor/osdu-cli',
    author='Equinor ASA',
    author_email='mhew@equinor.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    keywords='osdu',
    python_requires='>=3.6',
    packages=find_packages(exclude=['*tests*']),
    install_requires=[
        'knack==0.8.2',
        'msrest>=0.5.0',
        'msrestazure',
        'requests',
        'adal',
        'psutil',
        'portalocker',
        'six',
        "joblib",
        "tqdm"
    ],
    extras_require={
        'test': [
            'docutils==0.17.1',
            'flake8==3.9.2',
            'mock==4.0.3',
            'nose2==0.10.0',
            'pylint==2.7.2',
            'mock',
            'tox==3.24.1',
        ]
    },
    entry_points={
        'console_scripts': ['osducli=osducli.__main__:main']
    }
)
