# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import os.path
import shutil
import tempfile

from vincetools.compat import unittest


class StrTypeTests(unittest.TestCase):

    def _get(self):
        from vincetools.compat import str_type
        return str_type

    def test_unicode(self):
        self.assertIsInstance(u'foo', self._get())

    def test_str(self):
        self.assertIsInstance('foo', self._get())


class CompBytesTests(unittest.TestCase):

    def _get(self):
        from vincetools.compat import comp_bytes
        return comp_bytes

    @unittest.skip('wrong approach')
    def test_german_umlaut(self):
        self.assertEqual(self._get()('ä', 'utf-8'),
                         '\xc3\xa4')


class DIterKeysTests(unittest.TestCase):

    def _get(self):
        from vincetools.compat import d_iterkeys
        return d_iterkeys

    def test_is_not_a_list(self):
        result = self._get()({})
        self.assertNotIsInstance(result, list)

    def test_iterates_keys(self):
        result = self._get()({'a': 1, 'b': 0})
        self.assertEqual(sorted(result), ['a', 'b'])


class DIterValuesTests(unittest.TestCase):

    def _get(self):
        from vincetools.compat import d_itervalues
        return d_itervalues

    def test_is_not_a_list(self):
        result = self._get()({})
        self.assertNotIsInstance(result, list)

    def test_iterates_values(self):
        result = self._get()({'a': 1, 'b': 0})
        self.assertEqual(sorted(result), [0, 1])


class DIterItemsTests(unittest.TestCase):

    def _get(self):
        from vincetools.compat import d_iteritems
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
        from vincetools.compat import imap
        return imap

    def test_is_not_a_list(self):
        result = self._get()(lambda x: x, range(4))
        self.assertNotIsInstance(result, list)


class IFilterTests(unittest.TestCase):

    def _get(self):
        from vincetools.compat import ifilter
        return ifilter

    def test_is_not_a_list(self):
        result = self._get()(lambda _: True, range(4))
        self.assertNotIsInstance(result, list)


class ConfigParserTests(unittest.TestCase):

    def _get_cls(self):
        from vincetools.compat import ConfigParser
        return ConfigParser

    def test_read_string_available(self):
        cp = self._get_cls()()
        cp.read_string('\n'.join(['[foo]', 'bar = baz']))
        self.assertEqual(cp.get('foo', 'bar'), 'baz')


class GzipFileTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _get_cls(self):
        from vincetools.compat import GzipFile
        return GzipFile

    def test_writing(self):
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
        from vincetools.compat import ZipFile
        return ZipFile

    def test_as_context_manager(self):
        with tempfile.NamedTemporaryFile() as fp:
            with self._get()(fp.name, 'w'):
                pass
