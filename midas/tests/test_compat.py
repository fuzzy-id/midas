# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import tempfile

from midas.compat import unittest


class StrTypeTests(unittest.TestCase):

    def _get(self):
        from midas.compat import str_type
        return str_type

    def test_unicode(self):
        from midas.compat import PY3K
        if not PY3K:
            self.assertIsInstance(unicode('foo'), self._get())

    def test_str(self):
        self.assertIsInstance('foo', self._get())


class DIterKeysTests(unittest.TestCase):

    def _get(self):
        from midas.compat import d_iterkeys
        return d_iterkeys

    def test_is_not_a_list(self):
        result = self._get()({})
        self.assertNotIsInstance(result, list)

    def test_iterates_keys(self):
        result = self._get()({'a': 1, 'b': 0})
        self.assertEqual(sorted(result), ['a', 'b'])


class DIterValuesTests(unittest.TestCase):

    def _get(self):
        from midas.compat import d_itervalues
        return d_itervalues

    def test_is_not_a_list(self):
        result = self._get()({})
        self.assertNotIsInstance(result, list)

    def test_iterates_values(self):
        result = self._get()({'a': 1, 'b': 0})
        self.assertEqual(sorted(result), [0, 1])


class DIterItemsTests(unittest.TestCase):

    def _get(self):
        from midas.compat import d_iteritems
        return d_iteritems

    def test_is_not_a_list(self):
        result = self._get()({})
        self.assertNotIsInstance(result, list)

    def test_iterates_values(self):
        result = self._get()({'a': 1, 'b': 0})
        self.assertEqual(sorted(result), 
                         [('a', 1), ('b', 0)])


class IMapTests(unittest.TestCase):

    def _get(self):
        from midas.compat import imap
        return imap

    def test_is_not_a_list(self):
        result = self._get()(lambda x: x, range(4))
        self.assertNotIsInstance(result, list)


class IFilterTests(unittest.TestCase):

    def _get(self):
        from midas.compat import ifilter
        return ifilter

    def test_is_not_a_list(self):
        result = self._get()(lambda _: True, range(4))
        self.assertNotIsInstance(result, list)


class OrderedDictTests(unittest.TestCase):

    def _get_cls(self):
        from midas.compat import OrderedDict
        return OrderedDict

    def test_basic_behavior(self):
        data = [('foo', 1), ('bar', 2)]
        od = self._get_cls()(data)
        self.assertEqual(list(od.items()), data)


class UnittestTests(unittest.TestCase):

    def test_provides_assertRaisesRegex(self):
        with self.assertRaisesRegex(TypeError, 'list indices .*'):
            list()['foo']


class GzipFileTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _get_cls(self):
        from midas.compat import GzipFile
        return GzipFile

    def test_write_and_read(self):
        tmpfile = os.path.join(self.tmpd, 'foo.gz')
        with self._get_cls()(tmpfile, 'wb') as fp:
            fp.write(b'bar')

        self.assertEqual(os.listdir(self.tmpd), ['foo.gz'])
        self.assertNotEqual(os.stat(tmpfile).st_size, 0)

        with self._get_cls()(tmpfile) as fp:
            result = fp.readlines()
        self.assertEqual(result, [b'bar'])


class ZipFileTests(unittest.TestCase):

    def _get(self):
        from midas.compat import ZipFile
        return ZipFile

    def test_usable_as_context_manager(self):
        with tempfile.NamedTemporaryFile() as fp:
            with self._get()(fp.name, 'w'):
                pass
