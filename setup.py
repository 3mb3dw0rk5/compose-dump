#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
import sys


def find_version():
    for line in open(os.path.join('dump', '__init__.py'), 'rt').readlines():
        if line.startswith('__version__ = '):
            return line[len('__version__ = ')].strip()
    raise RuntimeError("Unable to find version string.")


install_requires = [x for x in open('requirements.txt').readlines() if x and not x.startswith('#')]

if sys.version_info < (3, 4):
    raise AssertionError('Requires Python 3.4 or later.')

setup(
    name='compose-dump',
    version=find_version(),
    description='Backup-tool for Docker-Compose projects',
    long_description=open('README.md').read(),
    classifiers=[  # TODO
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython'],
    # keywords= TODO
    url='https://github.com/funkyfuture/compose-dump',
    bugtrack_url='https://github.com/funkyfuture/compose-dump/issues',
    author='Frank Sachsenheim',
    author_email='funkyfuture@riseup.net',
    license='ISC',
    platforms=["any"],
    install_requires=install_requires,
    tests_require=[],  # TODO
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    test_suite='nose.collector',
    entry_points="""
    [console_scripts]
    compose-dump=dump.cli.main:main
    """,
)
