# -*- coding: utf-8 -*-

import sys

from setuptools import find_packages
from setuptools import setup

PY_VERSION = sys.version_info[:2]

INSTALL_REQUIRES = []

TESTS_REQUIRE = ['mock']

if PY_VERSION == (2, 6):
    TESTS_REQUIRE.append('unittest2')
    INSTALL_REQUIRES.append('argparse')
    INSTALL_REQUIRES.append('ordereddict')

setup(name='midas',
      version='0.1a1',
      packages=find_packages(),
      license='BSD-new',
      description='Data Mining on Alexa Top1M Data.',
      author='Thomas Bach',
      author_email='thbach@students.uni-mainz.de',
      install_requires=INSTALL_REQUIRES,
      tests_require=TESTS_REQUIRE,
      test_suite='midas.tests',
      entry_points={
        'console_scripts':
            ['md_fetch_crunchbase_companies=midas.scripts.fetch_crunchbase_companies:FetchCrunchbaseCompanies.cmd',
             'md_associate=midas.scripts.associate:Associate.cmd',
             'md_unzip_alexa_files=midas.scripts.unzip_alexa_files:UnzipAlexaFiles.cmd',
             'md_flatten_companies=midas.scripts.flatten_companies:FlattenCompanies.cmd',
             'md_make_restrictions=midas.scripts.sample_restriction:MakeSampleRestrictionShelve.cmd',
             'md_generate_samples=midas.scripts.generate_samples:GenerateSamples.cmd',
             ],
        },
      )
