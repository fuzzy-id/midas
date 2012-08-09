# -*- coding: utf-8 -*-

from StringIO import StringIO

import os.path

from crawlcrunch.compat import unittest

class CrawlCrunchTests(unittest.TestCase):

    def setUp(self):
        self.out_ = StringIO()

    def out(self, msg):
        self.out_.write(msg)

    def _get_target_class(self):
        from crawlcrunch.scripts.crawl_crunch_command import CrawlCrunchCommand
        return CrawlCrunchCommand

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
        self.assertTrue(
            out.startswith('You must provide one destination directory, not 2'))

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

    def test_dl_complete_runs(self):
        here = os.path.abspath(os.path.dirname(__file__))
        dl_complete = os.path.join(here, 
                                   '..', 'destinations', 'dl_complete')
        cmd = self._make_one(dl_complete)
        result = cmd.run()
        self.assertEqual(result, 0)

class MainTests(unittest.TestCase):

    def test_missing_argument(self):
        from crawlcrunch.scripts.crawl_crunch_command import main
        result = main(['crawlcrunch'], quiet=True)
        self.assertEqual(result, 2)
