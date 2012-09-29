# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import tempfile

from midas.tests import unittest

class GzipFileTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _get_cls(self):
        from midas.compat import GzipFile
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
