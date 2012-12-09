# -*- coding: utf-8 -*-

import sys

from setuptools import find_packages
from setuptools import setup

py_version = sys.version_info[:2]

install_requires = ['sqlalchemy']
install_requires.append('ordereddict')

tests_require = ['mock']

if py_version == (2, 6):
    tests_require.append('unittest2')
    install_requires.append('argparse')

setup(name='midas',
      version='0.1a1',
      packages=find_packages(),
      license='BSD-new',
      description='Data Mining on Alexa Top1M Data.',
      author='Thomas Bach',
      author_email='thbach@students.uni-mainz.de',
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='midas.tests',
      entry_points={
        'console_scripts':
            ['md_cc_update=midas.scripts.cc_update:main'],
        },
      )
