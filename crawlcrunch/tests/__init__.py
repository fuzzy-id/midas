# -*- coding: utf-8 -*-

import json
import logging
import mock
import os.path
import sys

from crawlcrunch.compat import StringIO
from crawlcrunch.compat import comp_bytes

py_version = sys.version_info[:2]

if py_version == (2, 6):  # pragma: no cover
    import unittest2 as unittest
else:
    import unittest

logging.basicConfig(level=logging.WARNING)


class DummyRoot(mock.Mock):

    def __init__(self, path=None):
        from crawlcrunch.model.local_files import LocalFilesRoot
        mock.Mock.__init__(self, spec=LocalFilesRoot)
        self.nodes = {}
        self.get = mock.Mock(side_effect=self._dummy_get)

    def _dummy_get(self, name):
        if self.nodes.get(name, None) is None:
            if name == 'companies':
                from crawlcrunch.model.local_files import CompanyList
                m = mock.Mock(spec=CompanyList)
            else:
                from crawlcrunch.model.local_files import Company
                m = mock.Mock(spec=Company)
            self.nodes[name] = m
        return self.nodes[name]

__here__ = os.path.abspath(os.path.dirname(__file__))
__test_examples__ = os.path.join(__here__, 'destinations')

EXAMPLES_PATH = {
    'company_files_empty': os.path.join(__test_examples__, 'company_files_empty'),
    'no_company_files': os.path.join(__test_examples__, 'no_company_files') }

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
