# -*- coding: utf-8 -*-

import sys

from setuptools import setup

py_version = sys.version_info[:2]

install_requires = ['sqlalchemy', ]

tests_require = ['mock', ]
if py_version == (2, 6):
    tests_require.append('unittest2')
    tests_require.append('argparse')

setup(name='crawlcrunch',
      version='0.2',
      description='Crawl crunchbase.com for companies information.',
      author='Thomas Bach',
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='crawlcrunch.tests',
      entry_points={
        'console_scripts':
            ['cc_update=crawlcrunch.scripts.cc_update:main', ],
        },
      )
