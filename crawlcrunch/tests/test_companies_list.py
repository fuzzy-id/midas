# -*- coding: utf-8 -*-

from crawlcrunch.compat import unittest
from crawlcrunch.tests import DestinationPaths

class CompaniesListTests(unittest.TestCase):

    def _get_target_class(self):
        from crawlcrunch.companies import CompaniesList
        return CompaniesList

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_list_creation(self):
        cl = self._make_one(DestinationPaths.dl_complete)
        cl.create_list()
        cl.companies.sort()
        self.assertEqual(cl.companies, [ 'de-revolutione',
                                         'group-laurier',
                                         'hiconversion',
                                         'pivotshare',
                                         'vaporstream',
                                         ])
