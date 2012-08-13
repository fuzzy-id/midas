# -*- coding: utf-8 -*-

import json
import logging
import mock
import os.path
import sys

from crawlcrunch.compat import StringIO
from crawlcrunch.compat import comp_bytes

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
    from io import BytesIO
    js = json.dumps(obj)
    b = comp_bytes(js, 'utf-8')
    buf = BytesIO(b)
    buf.seek(0)
    return buf

def prepare_url_open(url_open, return_dict):
    def side_effect(url):
        return _make_json_buffer(return_dict[url])
    url_open.side_effect = side_effect

def help_find_invalid_chars(company_name, line, column): # pragma: no cover
    from crawlcrunch.compat import url_open
    from crawlcrunch.model import LocalFilesDir
    root = LocalFilesDir('/tmp')
    company = root.get(company_name)
    resp = url_open(company.query_url())
    s = resp.read().decode('utf-8')
    splitted = s.split('\n')
    l = splitted[line-1]
    c = l[column-1]
    print('The entire line is:\n{0!r}'.format(l))
    print('The specific character is: {0!r}'.format(c))
    return l, c
