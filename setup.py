# -*- coding: utf-8 -*-

import sys

from setuptools import find_packages
from setuptools import setup

py_version = sys.version_info[:2]

install_requires = ['sqlalchemy', 
                    'vincetools']

tests_require = ['mock', ]
if py_version == (2, 6):
    tests_require.append('unittest2')
    install_requires.append('argparse')

setup(name='crawlcrunch',
      version='0.2',
      packages=find_packages(),
      license='BSD-new',
      description='Crawl crunchbase.com for companies information.',
      author='Thomas Bach',
      author_email='thbach@students.uni-mainz.de',
      dependency_links = [
        'http://github.com/fuzzy-id/vincetools/tarball/master#egg=vincetools-0.01dev'
        ],
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='crawlcrunch.tests',
      entry_points={
        'console_scripts':
            ['cc_update=crawlcrunch.scripts.cc_update:main', ],
        },
      )
