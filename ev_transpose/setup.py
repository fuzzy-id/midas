# -*- coding: utf-8 -*-

from setuptools import setup

import sys

PY_VERSION = sys.version_info[:2]

tests_require = []

if PY_VERSION == (2, 6):
    tests_require.append('unittest2')

setup(name='ev_transpose',
      version='0.0a1',
      description='Transpose time-series gathered over csv-files.',
      author='Thomas Bach',
      test_suite='ev_transpose.tests')
