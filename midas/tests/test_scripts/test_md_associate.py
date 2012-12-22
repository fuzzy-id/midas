# -*- coding: utf-8 -*-


from midas.tests import IntegrationTestCaseNG

import midas.tests as md_tests

@unittest.skip('this has to be reworked entirely')
class MdAssociateTests(IntegrationTestCaseNG):

    def _get_target_cls(self):
        from midas.scripts.md_associate import MDAssociate
        return MDAssociate

    def test_on_data(self):
        foo_c = self._make_company_json(self.companies_js[0])
        baz_bar_c = self._make_company_json(self.companies_js[1])
        self.assertEqual(self._call_cmd('-c', md_tests.TEST_CONFIG), 0)
        from midas.db import Association
        self.assertEqual(self.session.query(Association).count(), 1)
        result = self.session.query(Association).one()
        self.assertEqual(result.site, 'foo.example.com')

if __name__ == '__main__':  # pragma: no cover
    from midas.compat import unittest
    unittest.main()
