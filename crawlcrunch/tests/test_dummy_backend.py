# -*- coding: utf-8 -*-
from crawlcrunch.tests import unittest

class DummyRootTests(unittest.TestCase):

    def _make_one(self):
        from crawlcrunch.tests import DummyRoot
        return DummyRoot()

    def test_root_is_instance_of_local_files_dir_class(self):
        root = self._make_one()
        from crawlcrunch.model import LocalFilesDir
        self.assertIsInstance(root, LocalFilesDir)

    def test_get_companies_returns_instance_of_company_list(self):
        root = self._make_one()
        from crawlcrunch.model import CompanyList
        self.assertIsInstance(root.get('companies'), CompanyList)

    def test_get_a_company_returns_instance_of_company(self):
        root = self._make_one()
        company = root.get('facebook')
        from crawlcrunch.model import Company
        self.assertIsInstance(company, Company)

    def test_getting_the_same_company_returns_same_instance(self):
        root = self._make_one()
        c1 = root.get('a_company')
        c2 = root.get('a_company')
        self.assertIs(c1, c2)
