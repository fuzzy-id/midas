# -*- coding: utf-8 -*-

from setuptools import setup

import sys

PY_VERSION = sys.version_info[:2]

tests_require = ['mock']

if PY_VERSION == (2, 6):
    tests_require.append('unittest2')

setup(name='hbase',
      version='0.0a1',
      author='Thomas Bach',
      tests_require=tests_require,
      test_suite='hbase.tests')
