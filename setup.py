# -*- coding: utf-8 -*-

from setuptools import setup

import sys

install_requires = []

if sys.version_info[:2] == (2, 6):
    install_requires.append('unittest2')

setup(name='vincetools',
      version='0.1dev',
      packages=['vincetools'],
      license='BSD-new',
      test_suite='vincetools.tests',
      install_requires=install_requires)
