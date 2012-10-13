# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import tempfile

from vincetools.compat import unittest

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

class ConfigParserTests(unittest.TestCase):

    def _get_cls(self):
        from vincetools.compat import ConfigParser
        return ConfigParser

    def test_read_string_available(self):
        cp = self._get_cls()()
        cp.read_string('\n'.join(['[foo]', 'bar = baz']))
        self.assertEqual(cp.get('foo', 'bar'), 'baz')
