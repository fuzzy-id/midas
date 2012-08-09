# -*- coding: utf-8 -*-

from crawlcrunch.compat import unittest

class CompaniesListTests(unittest.TestCase):

    def _get_target_class(self):
        from crawlcrunch.companies import CompaniesList
        return CompaniesList

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)
