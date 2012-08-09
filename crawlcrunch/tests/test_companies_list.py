# -*- coding: utf-8 -*-

from crawlcrunch.compat import unittest
from crawlcrunch.tests import DestinationPaths

class CompaniesListTests(unittest.TestCase):

    def _get_target_class(self):
        from crawlcrunch.companies import CompaniesList
        return CompaniesList

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_list_creation_when_all_companies_files_present(self):
        cl = self._make_one(DestinationPaths.dl_complete)
        cl.create_list()
        self.assertEqual(cl.companies, [])

    def test_list_creation_when_companies_missing(self):
        cl = self._make_one(DestinationPaths.no_companies)
        cl.create_list()
        self.assertEqual(cl.companies, [ 'de-revolutione',
                                         'group-laurier',
                                         'hiconversion',
                                         'pivotshare',
                                         'vaporstream',
                                         ])
