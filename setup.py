# -*- coding: utf-8 -*-

from setuptools import setup

import sys

PY_VERSION = sys.version_info[:2]

install_requires = []

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
            ['md_alexa_to_key=midas.transform:run_alexa_to_key',
             'md_key_to_files=midas.transform:run_key_to_files',
             'md_alexa_to_names_and_one=midas.analyze:run_alexa_to_names_and_one',
             'md_sum_values=midas.analyze:run_sum_names',
             'md_find_strange_names=midas.assign:find_strange_names']})
