# -*- coding: utf-8 -*-

from midas.compat import GzipFile
from midas.tests import unittest

import datetime
import os.path
import shutil
import tempfile

class LookUpTests(unittest.TestCase):

    a_date = datetime.date(1900, 1, 1)
    one_day = datetime.timedelta(days=1)

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _run_it(self, name, key_dir):
        from midas.model import lookup_ranking
        return lookup_ranking(name, key_dir)

    def test_only_one_entry(self):
        from midas import RankEntry
        data = [RankEntry('foo', self.a_date, 1),
                RankEntry('foo', self.a_date + self.one_day, 1),
                RankEntry('foo', self.a_date + self.one_day*2, 1),
                RankEntry('foo', self.a_date + self.one_day*3, 1)]
        key_file = os.path.join(self.tmpd, '{0}.gz'.format(data[0].key))
        with GzipFile(key_file, 'wb') as fp:
            for entry in data:
                fp.write(('{0}\n'.format(entry.format_std)).encode())
        result = self._run_it('foo', self.tmpd)
        self.assertEqual(list(map(str, data)), list(map(str, result)))
        
    def test_other_entries_in_front(self):
        from midas import RankEntry
        bars = [RankEntry('bar', self.a_date, 1),
                RankEntry('bar', self.a_date + self.one_day, 1),
                RankEntry('bar', self.a_date + self.one_day*2, 1),
                RankEntry('bar', self.a_date + self.one_day*3, 1)]
        foos = [RankEntry('foo', self.a_date, 1),
                RankEntry('foo', self.a_date + self.one_day, 1),
                RankEntry('foo', self.a_date + self.one_day*2, 1),
                RankEntry('foo', self.a_date + self.one_day*3, 1)]
        data = bars + foos
        key_file = os.path.join(self.tmpd, 
                                '{0}.gz'.format(RankEntry.make_key('foo')))
        with GzipFile(key_file, 'wb') as fp:
            for entry in data:
                fp.write(('{0}\n'.format(entry.format_std)).encode())
        result = self._run_it('foo', self.tmpd)
        self.assertEqual(list(map(str, foos)), list(map(str, result)))
        
if __name__ == '__main__':  # pragma: no cover
    unittest.main()
