# -*- coding: utf-8 -*-
from crawlcrunch.tests import unittest


class DummyRootTests(unittest.TestCase):

    def _make_one(self):
        from crawlcrunch.tests import DummyRoot
        return DummyRoot()

    def test_root_is_instance_of_local_files_dir_class(self):
        root = self._make_one()
        from crawlcrunch.model.local_files import LocalFilesRoot
        self.assertIsInstance(root, LocalFilesRoot)

    def test_get_companies_returns_instance_of_company_list(self):
        root = self._make_one()
        from crawlcrunch.model.local_files import CompanyList
        self.assertIsInstance(root.get('companies'), CompanyList)
