# -*- coding: utf-8 -*-

from midas.compat import unittest


class DummyRootTests(unittest.TestCase):

    def _make_one(self):
        from midas.tests import DummyRoot
        return DummyRoot()

    def test_root_is_instance_of_local_files_dir_class(self):
        root = self._make_one()
        from midas.crunchbase_crawler import LocalFilesRoot
        self.assertIsInstance(root, LocalFilesRoot)

    def test_get_companies_returns_instance_of_company_list(self):
        root = self._make_one()
        from midas.crunchbase_crawler import CompanyList
        self.assertIsInstance(root.get('companies'), CompanyList)
