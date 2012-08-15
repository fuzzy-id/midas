# -*- coding: utf-8 -*-

import json
import os
import os.path
import shutil
import tempfile

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import StringIO
from crawlcrunch.tests import DestinationPaths
from crawlcrunch.tests import prepare_url_open
from crawlcrunch.tests import unittest

import mock


class CrawlCrunchTests(unittest.TestCase):

    def setUp(self):
        self.out_ = StringIO()

    def out(self, msg):
        self.out_.write(msg)

    def _get_target_class(self):
        from crawlcrunch.scripts.cc_update import CCUpdateCommand
        return CCUpdateCommand

    def _make_one(self, *args):
        effargs = ['crawlcrunch', ]
        effargs.extend(args)
        cmd = self._get_target_class()(effargs)
        cmd.out = self.out
        return cmd

    def test_missing_argument(self):
        cmd = self._make_one()
        result = cmd.run()
        self.assertEqual(result, 2)
        out = self.out_.getvalue()
        self.assertTrue(
            out.startswith('You must provide a destination directory'))

    def test_too_much_arguments(self):
        cmd = self._make_one('one', 'two', )
        result = cmd.run()
        self.assertEqual(result, 2)
        out = self.out_.getvalue()
        self.assertTrue(out.startswith(''.join(('You must ',
                                                'provide one ',
                                                'destination ',
                                                'directory, ',
                                                'not 2'))))

    def test_non_existent_path(self):
        cmd = self._make_one((os.path.join('non',
                                           'existent',
                                           'path', )))
        result = cmd.run()
        self.assertEqual(result, 2)
        out = self.out_.getvalue()
        self.assertTrue(
            out.startswith(
                "The directory 'non/existent/path' does not exist"))
        self.assertTrue(out.endswith("Please, create it first."))


class MainTests(unittest.TestCase):

    def test_missing_argument(self):
        from crawlcrunch.scripts.cc_update import main
        result = main(['cc_update'], quiet=True)
        self.assertEqual(result, 2)


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _make_one(self, path):
        from crawlcrunch.scripts.cc_update import CCUpdateCommand
        return CCUpdateCommand(['cc_update', path])

    @mock.patch('crawlcrunch.model.url_open')
    def test_on_empty_companies_list(self, url_open):
        url_return = (
            {'http://api.crunchbase.com/v/1/companies.js': []})
        prepare_url_open(url_open, url_return)
        cmd = self._make_one(self.tmpd)
        result = cmd.run()
        self.assertEqual(result, 0)
        url_open.assert_called_once_with(
            'http://api.crunchbase.com/v/1/companies.js')
        listing = os.listdir(self.tmpd)
        self.assertEqual(listing, ['companies.json.gz'])
        companies_file = os.path.join(self.tmpd,
                                      'companies.json.gz')
        self.assertTrue(os.path.isfile(companies_file))
        with GzipFile(companies_file) as fp:
            self.assertEqual(json.load(fp), [])

    @mock.patch('crawlcrunch.model.url_open')
    def test_on_companies_list_with_elements(self, url_open):
        prepare_url_open(
            url_open,
            {'http://api.crunchbase.com/v/1/companies.js': (
                    [{'permalink': 'foo', },
                     {'permalink': 'bar', }]),
             'http://api.crunchbase.com/v/1/company/foo.js': (
                    ['some_foo']),
             'http://api.crunchbase.com/v/1/company/bar.js': (
                    ['some_bar'])})
        cmd = self._make_one(self.tmpd)
        result = cmd.run()
        self.assertEqual(result, 0)
        url_open.assert_called_with(
            'http://api.crunchbase.com/v/1/company/bar.js')
        listing = os.listdir(self.tmpd)
        listing.sort()
        self.assertEqual(listing, ['bar.json.gz',
                                   'companies.json.gz',
                                   'foo.json.gz',
                                   ])

        with GzipFile(os.path.join(self.tmpd,
                                   'companies.json.gz')) as fp:
            self.assertEqual(json.load(fp), [{'permalink': 'foo'},
                                             {'permalink': 'bar'}])
        with GzipFile(os.path.join(self.tmpd,
                                   'bar.json.gz')) as fp:
            self.assertEqual(json.load(fp), ['some_bar', ])
        with GzipFile(os.path.join(self.tmpd,
                                   'foo.json.gz')) as fp:
            self.assertEqual(json.load(fp), ['some_foo', ])

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
