# -*- coding: utf-8 -*-

from setuptools import setup

import sys

PY_VERSION = sys.version_info[:2]

install_requires = ['crawlcrunch']
tests_require = ['mock']

if PY_VERSION == (2, 6):
    install_requires.append('argparse')
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
            ['md_launch=midas.scripts.md_launch:MDLaunch.cmd',
             'md_alexa_to_key=midas.scripts.alexa_to_key_files:AlexaToKey.cmd',
             'md_key_to_files=midas.scripts.alexa_to_key_files:KeyToFiles.cmd',
             'md_alexa_to_names_and_one=midas.scripts.alexa_count_names:AlexaToNamesAndOne.cmd',
             'md_sum_values=midas.scripts.alexa_count_names:SumValues.cmd']})
