# -*- coding: utf-8 -*-

from io import BytesIO

import collections
import json
import logging
import mock
import os.path
import sys

from crawlcrunch.compat import PY_VERSION
from crawlcrunch.compat import StringIO
from crawlcrunch.compat import comp_bytes

if PY_VERSION == (2, 6):  # pragma: no cover
    import unittest2 as unittest
else:
    import unittest


logging.basicConfig(level=logging.CRITICAL)

__here__ = os.path.abspath(os.path.dirname(__file__))
__test_examples__ = os.path.join(__here__, 'destinations')
EXAMPLES_PATH = {
    'company_files_empty': os.path.join(__test_examples__, 
                                        'company_files_empty'),
    'no_company_files': os.path.join(__test_examples__, 
                                     'no_company_files') }
MEM_DB = 'sqlite:///:memory:'

COMPANIES_URL = 'http://api.crunchbase.com/v/1/companies.js?api_key=vqrwexbhj9s2d7fbzzj9cg57'
FOO_URL = 'http://api.crunchbase.com/v/1/company/foo.js?api_key=vqrwexbhj9s2d7fbzzj9cg57'
BAR_URL = 'http://api.crunchbase.com/v/1/company/bar.js?api_key=vqrwexbhj9s2d7fbzzj9cg57'

def DummyRoot(path=None):
    from crawlcrunch.model.local_files import LocalFilesRoot
    dr = mock.Mock(spec=LocalFilesRoot, path=path)
    dcl = DummyCompanyList(path)

    def dummy_get(name):
        if name == 'companies':
            return dcl
        raise NotImplementedError(
            "Unknown class '{0}'".format(name))  # pragma: no cover

    dr.get.side_effect = dummy_get
    return dr

def DummyCompanyList(path=None):
    from crawlcrunch.model.local_files import CompanyList
    dcl = mock.Mock(spec=CompanyList)
    d = dict()

    def side_effect(name):
        if not name in d:
            d[name] = DummyCompany(name)
        return d[name]

    dcl.get.side_effect = side_effect
    return dcl

def DummyCompany(name='dummy_company'):
    from crawlcrunch.model.local_files import Company
    dc = mock.Mock(spec=Company)
    dc.name = name
    return dc

def _make_json_buffer(obj):
    buf = BytesIO(comp_bytes(json.dumps(obj), 'utf-8'))
    buf.seek(0)
    return buf

def prepare_url_open(urlopen, return_dict):

    def side_effect(url):
        return _make_json_buffer(return_dict[url])

    urlopen.side_effect = side_effect
