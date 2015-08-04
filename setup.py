#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
from setuptools import setup, find_packages
import codecs
import os
import re
import sys


def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = [
    # compose
    'docopt >= 0.6.1, < 0.7',
    'PyYAML >= 3.10, < 4',
    'requests >= 2.6.1, < 2.7',
    'texttable >= 0.8.1, < 0.9',
    'websocket-client >= 0.32.0, < 1.0',
    'docker-py >= 1.3.1, < 1.4',
    'dockerpty >= 0.3.4, < 0.4',
    'six >= 1.3.0, < 2',
    # dump
    'path.py >= 7.6',
]


tests_require = [
    'mock >= 1.0.1',
    'nose',
    'flake8',
]


if sys.version_info < (2, 7):
    tests_require.append('unittest2')


setup(
    name='compose-dump',
    version=find_version("dump", "__init__.py"),
    description='Backup-tool for Docker-Compose',
    url='https://github.com/funkyfuture/compose-dump',
    author='Frank Sachsenheim',
    license='Apache License 2.0',
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    test_suite='nose.collector',
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points="""
    [console_scripts]
    compose-dump=dump.cli.main:main
    """,
)
