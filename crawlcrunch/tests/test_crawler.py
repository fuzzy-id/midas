# -*- coding: utf-8 -*-

from StringIO import StringIO

import json
import os.path
import shutil
import tempfile
import threading

import mock

from crawlcrunch.compat import unittest
from crawlcrunch.compat import GzipFile

class CrawlerTests(unittest.TestCase):

    def _get_target_class(self):
        from crawlcrunch.crawler import Crawler
        return Crawler

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

class CompanyFetcherTests(unittest.TestCase):

    def _get_target_class(self):
        from crawlcrunch.crawler import CompanyFetcher
        return CompanyFetcher

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_url_generation(self):
        cf = self._make_one('facebook', 'dst', threading.Semaphore(1))
        expected = 'http://api.crunchbase.com/v/1/company/facebook.js'
        self.assertEqual(cf.query_url(), expected)

class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    @mock.patch('urllib2.urlopen')
    def test_run_method(self, urlopen):
        content = StringIO()
        json.dump({'foo': 'bar'}, content)
        content.seek(0)
        urlopen.return_value = content
        dump_file = os.path.join(self.tmpd, 'dump.json.gz')
        from crawlcrunch.crawler import CompanyFetcher
        cf = CompanyFetcher('facebook', 
                            dump_file,
                            threading.Semaphore(1))
        cf.run()
        urlopen.assert_called_once_with(
            'http://api.crunchbase.com/v/1/company/facebook.js'
            )
        with GzipFile(dump_file) as fp:
            self.assertEqual(json.load(fp), {'foo': 'bar'})

if __name__ == '__main__': # pragma: no cover
    unittest.main()
