# -*- coding: utf-8 -*-

from setuptools import setup

import sys

PY_VERSION = sys.version_info[:2]

tests_require = ['mock']

if PY_VERSION == (2, 6):
    tests_require.append('unittest2')

setup(name='midas',
      version='0.0a1',
      description='Try to get some useful information from Top1M.',
      author='Thomas Bach',
      tests_require=tests_require,
      test_suite='midas.tests',
      entry_points={
        'console_scripts':
            ['md_top1m_to_sha1=midas.map_to_sha1:mapper',
             'md_top1m_to_db=midas.model:push_to_db']
        })
