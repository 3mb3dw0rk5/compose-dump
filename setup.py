#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys


install_requires = [x for x in open('requirements.txt').readlines() if x and not x.startswith('#')]

if sys.version_info < (3, 4):
    raise AssertionError('Requires Python 3.4 or later.')

setup(
    name='compose-dump',
    version='0.1-beta2',
    description='Backup tool for Docker Compose projects',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Archiving :: Backup'],
    keywords='docker-compose backup archiving',
    url='http://compose-dump.rtfd.io/',
    bugtrack_url='https://github.com/funkyfuture/compose-dump/issues',
    author='Frank Sachsenheim',
    author_email='funkyfuture@riseup.net',
    license='ISC',
    platforms=["any"],
    install_requires=install_requires,
    tests_require=[],  # TODO
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    entry_points="""
    [console_scripts]
    compose-dump=compose_dump.main:main
    """,
)
