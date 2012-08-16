# -*- coding: utf-8 -*-

from sqlalchemy import create_engine

from crawlcrunch.tests import unittest
from crawlcrunch.model.db import Session
from crawlcrunch.model.db import Base

class FundingTests(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        self.session = Session()

    def _get_target_class(self):
        from crawlcrunch.model.db import FundingRound
        return FundingRound

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_session_tests(self):
        f = self._make_one()
        self.assertIsNone(f.id)
        self.assertIsNone(f.funded_day)
        self.session.add(f)
        self.session.flush()
        self.assertIsNotNone(f.id)

    def test_instantiation_by_keywords(self):
        f = self._make_one(funded_day=80, funded_year=50)
        self.assertEqual(f.funded_day, 80)
        self.assertEqual(f.funded_year, 50)

    def test_instantiation_by_dict(self):
        f = self._make_one(**{'funded_day': 80,
                              'funded_year': 50})
        self.assertEqual(f.funded_day, 80)
        self.assertEqual(f.funded_year, 50)

    def test_with_not_available_keywords(self):
        with self.assertRaises(TypeError):
            self._make_one(foo='bar')
        with self.assertRaises(TypeError):
            self._make_one(**{'foo': 'bar'})
        
class CompanyTests(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        self.session = Session()

    def _get_target_class(self):
        from crawlcrunch.model.db import Company
        return Company

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_company_with_fundings_list(self):
        from crawlcrunch.model.db import FundingRound
        f1 = FundingRound(funded_year=40)
        f2 = FundingRound(funded_year=30)
        c = self._make_one(funding_rounds=[f1, f2])
        self.session.add(c)
        self.session.flush()
        result = self.session.query(self._get_target_class()).get(1)
        self.assertIs(result, c)
        self.assertIs(result.funding_rounds[0], f1)
        self.assertIs(result.funding_rounds[1], f2)
        
