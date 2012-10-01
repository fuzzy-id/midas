# -*- coding: utf-8 -*-

from setuptools import setup

import sys

PY_VERSION = sys.version_info[:2]

install_requires = ['crawlcrunch']

if PY_VERSION == (2, 6):
    install_requires.append('argparse')

tests_require = ['mock']

if PY_VERSION == (2, 6):
    tests_require.append('unittest2')

setup(name='midas',
      version='0.0a1',
      description='Try to get some useful information from Top1M.',
      author='Thomas Bach',
      dependency_links = ['http://github.com/fuzzy-id/crawlcrunch/tarball/master#egg=crawlcrunch'],
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='midas.tests',
      entry_points={
        'console_scripts':
            ['md_alexa_to_key=midas.transform:AlexaToKey.cmd',
             'md_key_to_files=midas.transform:KeyToFiles.cmd',
             'md_alexa_to_names_and_one=midas.analyze:AlexaToNamesAndOne.cmd',
             'md_sum_values=midas.analyze:SumValues.cmd']})
