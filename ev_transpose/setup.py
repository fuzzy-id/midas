# -*- coding: utf-8 -*-

from setuptools import setup

import sys

PY_VERSION = sys.version_info[:2]

tests_require = ['mock']

if PY_VERSION == (2, 6):
    tests_require.append('unittest2')
    tests_require.append('argparse')

setup(name='ev_transpose',
      version='0.0a1',
      description='Transpose time-series gathered over csv-files.',
      author='Thomas Bach',
      tests_require=tests_require,
      test_suite='ev_transpose.tests',
      entry_points={
        'console_scripts':
            ['ev_transpose=ev_transpose.script:main']})
