# -*- coding: utf-8 -*-

from midas.tests.test_scripts import IntegrationTestCaseNG

class MdAssociateTests(IntegrationTestCaseNG):

    def _get_target_cls(self):
        from midas.scripts.md_associate import MDAssociate
        return MDAssociate

    def test_on_data(self):
        foo_c = self._make_company_json(self.companies_js[0])
        baz_bar_c = self._make_company_json(self.companies_js[1])
        self.assertEqual(self._call_cmd(), 0)
        from midas.db import Association
        self.assertEqual(self.session.query(Association).count(), 2)
        result = self.session.query(Association).filter(company=foo_c).one()
        self.assertEqual(result.site, 'foo.example.com')
