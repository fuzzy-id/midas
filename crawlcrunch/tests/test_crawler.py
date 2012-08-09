# -*- coding: utf-8 -*-

from crawlcrunch.compat import unittest

class CrawlerTests(unittest.TestCase):

    def _get_target_class(self):
        from crawlcrunch.crawler import Crawler
        return Crawler

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)