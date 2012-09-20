# -*- coding: utf-8 -*-

from setuptools import setup

import sys

PY_VERSION = sys.version_info[:2]

install_requires = ['sqlalchemy']

if PY_VERSION == (2, 6):
    install_requires.append('argparse')

tests_require = ['mock']

if PY_VERSION == (2, 6):
    tests_require.append('unittest2')

setup(name='midas',
      version='0.0a1',
      description='Try to get some useful information from Top1M.',
      author='Thomas Bach',
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='midas.tests',
      entry_points={
        'console_scripts':
            ['md_alexa_to_sha1=midas.transform:run_alexa_to_sha1',
             'md_sort_sha1=midas.transform:sort_sha1',
             'md_top1m_to_db=midas.transform:push_to_db',
             'md_find_strange_names=midas.assign:find_strange_names']})
