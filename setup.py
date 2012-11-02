# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

import sys

PY_VERSION = sys.version_info[:2]

install_requires = ['vincetools', 'crawlcrunch', 'mrjob']
tests_require = ['mock']

if PY_VERSION == (2, 6):
    install_requires.append('argparse')
    tests_require.append('unittest2')

setup(name='midas',
      version='0.0a1',
      packages=find_packages(),
      license='BSD-new',
      description='Try to get some useful information from Top1M.',
      author='Thomas Bach',
      author_email='thbach@students.uni-mainz.de',
      dependency_links = [
        'http://github.com/fuzzy-id/crawlcrunch/tarball/master#egg=crawlcrunch-0.2',
        'http://github.com/fuzzy-id/vincetools/tarball/master#egg=vincetools-0.01dev'
        ],
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='midas.tests',
      entry_points={
        'console_scripts':
            ['md_config=midas.scripts.md_config:MDConfig.cmd',
             'md_launch=midas.scripts.md_launch:MDLaunch.cmd',
             'md_alexa_to_key=midas.scripts.alexa_to_key_files:AlexaToKey.cmd',
             'md_key_to_files=midas.scripts.alexa_to_key_files:KeyToFiles.cmd',
             'md_alexa_to_names_and_one=midas.scripts.alexa_count_sites:AlexaCountSitesJob.run',
             'md_sum_values=midas.scripts.alexa_count_names:SumValues.cmd']})
