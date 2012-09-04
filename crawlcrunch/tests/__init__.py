# -*- coding: utf-8 -*-

from io import BytesIO

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


logging.basicConfig(level=logging.WARNING)

__here__ = os.path.abspath(os.path.dirname(__file__))
__test_examples__ = os.path.join(__here__, 'destinations')
EXAMPLES_PATH = {
    'company_files_empty': os.path.join(__test_examples__, 
                                        'company_files_empty'),
    'no_company_files': os.path.join(__test_examples__, 
                                     'no_company_files') }


class DummyRoot(mock.Mock):

    def __init__(self, path=None):
        from crawlcrunch.model.local_files import LocalFilesRoot
        mock.Mock.__init__(self, spec=LocalFilesRoot)
        self.get = mock.Mock(side_effect=self._dummy_get)

    def _dummy_get(self, name):
        if name == 'companies':
            from crawlcrunch.model.local_files import CompanyList
            return mock.Mock(spec=CompanyList)
        raise NotImplementedError("Unknown class '{0}'".format(name))


def _make_json_buffer(obj):
    buf = BytesIO(comp_bytes(json.dumps(obj), 'utf-8'))
    buf.seek(0)
    return buf

def prepare_url_open(urlopen, return_dict):
    def side_effect(url):
        return _make_json_buffer(return_dict[url])
    urlopen.side_effect = side_effect
