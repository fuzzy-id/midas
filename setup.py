# -*- coding: utf-8 -*-

import sys

from setuptools import find_packages
from setuptools import setup

PY_VERSION = sys.version_info[:2]

INSTALL_REQUIRES = ['sqlalchemy']
INSTALL_REQUIRES.append('ordereddict')

TESTS_REQUIRE = ['mock']

if PY_VERSION == (2, 6):
    TESTS_REQUIRE.append('unittest2')
    INSTALL_REQUIRES.append('argparse')

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
            ['md_cc_update=midas.scripts.cc_update:main',
             'md_associate=midas.scripts.md_associate:MDAssociate.cmd',
             'md_alexa_zip_to_gzip=midas.scripts.alexa_zip_to_gzip:AlexaZipToGzip.cmd',
             ],
        },
      )
