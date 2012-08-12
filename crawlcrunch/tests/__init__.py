# -*- coding: utf-8 -*-

import json
import logging
import mock
import os.path
import sys

from crawlcrunch.compat import StringIO

py_version = sys.version_info[:2]

if py_version == (2, 6): # pragma: no cover
    import unittest2 as unittest
else:
    import unittest

logging.basicConfig(level=logging.WARNING)

class DummyRoot(mock.Mock):

    def __init__(self, path=None):
        from crawlcrunch.model import LocalFilesDir
        mock.Mock.__init__(self, spec=LocalFilesDir)
        self.nodes = {}
        self.get = mock.Mock(side_effect=self._dummy_get)

    def _dummy_get(self, name):
        if self.nodes.get(name, None) is None:
            if name == 'companies':
                from crawlcrunch.model import CompanyList
                m = mock.Mock(spec=CompanyList)
            else:
                from crawlcrunch.model import Company
                m = mock.Mock(spec=Company)
            self.nodes[name] = m
        return self.nodes[name]
    
class DestinationPaths(object):

    here = os.path.abspath(os.path.dirname(__file__))
    destinations = os.path.join(here, 'destinations')
    companies_empty = os.path.join(destinations, 'companies_empty')
    no_companies = os.path.join(destinations, 'no_companies')

def _make_json_buffer(obj):
    buf = StringIO()
    json.dump(obj, buf)
    buf.seek(0)
    return buf

def prepare_url_open(url_open, return_dict):
    def side_effect(url):
        return _make_json_buffer(return_dict[url])
    url_open.side_effect = side_effect

