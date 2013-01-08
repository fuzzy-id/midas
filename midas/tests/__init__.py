# -*- coding: utf-8 -*-

from io import BytesIO

import json
import logging
import os.path

import mock

from midas.compat import comp_bytes


logging.basicConfig(level=logging.CRITICAL)


_here = os.path.abspath(os.path.dirname(__file__))
_test_data_home = os.path.join(_here, '..', '..', 'test_data')

TEST_DATA_PATH = {
    'alexa_zip_files': os.path.join(_test_data_home, 'alexa_zip_files'),
    'alexa_files': os.path.join(_test_data_home, 'alexa_files'),
    'site_count': os.path.join(_test_data_home, 'site_count'),
    'crunchbase': os.path.join(_test_data_home, 'crunchbase'),
    'companies': os.path.join(_test_data_home, 'companies'),
    'crunchbase_companies': os.path.join(_test_data_home, 
                                         'crunchbase_companies'),
    }

__test_examples__ = TEST_DATA_PATH['crunchbase']
EXAMPLES_PATH = {
    'company_files_empty': os.path.join(__test_examples__, 'company_files_empty'),
    'no_company_files': os.path.join(__test_examples__, 'no_company_files')
    }

COMPANIES_URL = 'http://api.crunchbase.com/v/1/companies.js?api_key=vqrwexbhj9s2d7fbzzj9cg57'
FOO_URL = 'http://api.crunchbase.com/v/1/company/foo.js?api_key=vqrwexbhj9s2d7fbzzj9cg57'
BAR_URL = 'http://api.crunchbase.com/v/1/company/bar.js?api_key=vqrwexbhj9s2d7fbzzj9cg57'

def DummyCompanyList(path=None):
    from midas.crunchbase_crawler import CompanyList
    dcl = mock.Mock(spec=CompanyList)
    d = dict()

    def side_effect(name):
        if not name in d:
            d[name] = DummyCompany(name)
        return d[name]

    dcl.get.side_effect = side_effect
    return dcl

def DummyCompany(name='dummy_company'):
    from midas.crunchbase_company import Company
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
