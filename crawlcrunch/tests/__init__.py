# -*- coding: utf-8 -*-

import logging
import os.path
import sys

py_version = sys.version_info[:2]

if py_version == (2, 6): # pragma: no cover
    import unittest2 as unittest
else:
    import unittest

logging.basicConfig(level=logging.WARNING)

class DestinationPaths(object):

    here = os.path.abspath(os.path.dirname(__file__))
    destinations = os.path.join(here, 'destinations')
    companies_empty = os.path.join(destinations, 'companies_empty')
    no_companies = os.path.join(destinations, 'no_companies')
