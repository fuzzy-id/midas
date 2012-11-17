# -*- coding: utf-8 -*-

from midas.tests import ConfiguredDBTestCase

class AssociationTests(ConfiguredDBTestCase):
    " Test the proper working of the Association class. "

    def test_backref_on_company(self):
        foo_comp = self._make_company_json(self.companies_js[0])
        from midas.db import Association
        assoc = Association(site='foo.example.com', company=foo_comp)
        result = self.session.query(Association).one()
        self.assertIs(result, assoc)
        from midas.db import Company
        result = self.session.query(Company).one()
        self.assertIs(result.site, assoc)


class IterCompaniesTests(ConfiguredDBTestCase):

    def _run_it(self):
        from midas.db import iter_all_companies
        return list(iter_all_companies())

    def test_iter_all_companies(self):
        c1 = self._make_company_json({})
        c2 = self._make_company_json({})
        self.assertEqual(self._run_it(), [c1, c2])


class IterInteresstingCompaniesTests(ConfiguredDBTestCase):

    def _run_it(self):
        from midas.db import iter_interesting_companies
        return list(iter_interesting_companies())

    def test_function_runs(self):
        c = self._make_company_json({})
        self.assertEqual(self._run_it(), [])

    def test_company_w_two_funding_rounds_is_returned_once(self):
        c = self._make_company_json(self.companies_js[0])
        self.assertEqual(self._run_it(), [c])
