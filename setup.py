# -*- coding: utf-8 -*-

import sys

from setuptools import setup

py_version = sys.version_info[:2]

tests_require = ['mock', ]
if py_version == (2, 6):
    tests_require.append('unittest2')

setup(name='crawlcrunch',
      version='0.1dev1',
      description='Crawl crunchbase.com for companies information.',
      author='Thomas Bach',
      tests_require=tests_require,
      test_suite='crawlcrunch.tests',
      entry_points={
        'console_scripts': ['crawlcrunch=crawlcrunch.scripts.crawlcrunch:main', ],
        },
      )
