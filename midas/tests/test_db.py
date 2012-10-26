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

