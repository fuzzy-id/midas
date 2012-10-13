# -*- coding: utf-8 -*-

from vincetools.compat import unittest

class KeyFuncTestCase(unittest.TestCase):

    @property
    def _keyfunc(self):
        from midas.tools import get_key
        return get_key

    sequence = [ '{0}\tblah'.format(e) 
                 for e in ['foo'] * 5 + ['bar'] * 3 ]


class GroupByKeyTests(KeyFuncTestCase):

    def _run_it(self, iterable):
        from midas.tools import group_by_key
        return [ list(block) 
                 for block in group_by_key(iterable, self._keyfunc) ]

    def test_on_empty_sequence(self):
        self.assertEqual([], self._run_it([]))

    def test_on_sequence(self):
        self.assertEqual([['foo\tblah']*5, ['bar\tblah']*3], 
                         self._run_it(self.sequence))
        
    def test_single_key(self):
        result = [ list(block) for block in self._run_it(['foo\t3']*1) ]
        self.assertEqual([['foo\t3']*1], result)


class CountByKeyTests(KeyFuncTestCase):

    def _run_it(self, iterable):
        from midas.tools import count_by_key
        return count_by_key(iterable, self._keyfunc)

    def test_on_empty_sequence(self):
        self.assertEqual(dict(), self._run_it([]))

    def test_on_sequence(self):
        self.assertEqual(dict([('foo', 5), 
                               ('bar', 3)]),
                         self._run_it(self.sequence))


class CollectByKeyTests(KeyFuncTestCase):

    def _run_it(self, iterable):
        from midas.tools import collect_by_key
        return collect_by_key(iterable, self._keyfunc)

    def test_on_empty_sequence(self):
        self.assertEqual(dict(), self._run_it([]))

    def test_on_sequence(self):
        self.assertEqual(self._run_it(self.sequence),
                         dict([('foo', ['foo\tblah']*5),
                               ('bar', ['bar\tblah']*3)]))
                         

class DomainTests(unittest.TestCase):

    def _run_it(self, company_or_site):
        from midas.tools import domain
        return domain(company_or_site)

    def test_on_company(self):
        from midas.tools import Company
        c = Company(homepage_url='http://example.com/foo')
        self.assertEqual(self._run_it(c), 'example.com')

    def test_on_site(self):
        from midas.tools import Company
        self.assertEqual(self._run_it('example.com/foo'), 'example.com')

    def test_on_object(self):
        with self.assertRaises(TypeError):
            self._run_it(object())


class DBTestCase(unittest.TestCase):

    def setUp(self):
        from crawlcrunch.model.db import Base
        from crawlcrunch.model.db import Session
        from crawlcrunch.model.db import create_engine
        import midas.tools as md_tools
        engine = create_engine('sqlite:///:memory:')
        Session.remove()
        Session.configure(bind=engine)
        Base.metadata.create_all(engine, checkfirst=False)
        md_tools._session = Session()

    def tearDown(self):
        from crawlcrunch.model.db import Session
        Session.remove()

    def _make_company(self, *args, **kwargs):
        from midas.tools import Company
        c = Company(*args, **kwargs)
        from midas.tools import db_session
        sess = db_session()
        sess.add(c)
        return c


class IterCompaniesTests(DBTestCase):

    def _run_it(self):
        from midas.tools import iter_all_companies
        return list(iter_all_companies())

    def test_iter_all_companies(self):
        c1 = self._make_company()
        c2 = self._make_company()
        self.assertEqual(self._run_it(), [c1, c2])

class IterInteresstingCompaniesTests(DBTestCase):

    def _run_it(self):
        from midas.tools import iter_interesting_companies
        return list(iter_interesting_companies())

    def test_function_runs(self):
        c = self._make_company()
        self.assertEqual(self._run_it(), [])
