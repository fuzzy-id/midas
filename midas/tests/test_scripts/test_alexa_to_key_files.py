# -*- coding: utf-8 -*-

import datetime
import os
import random
import shutil
import tempfile

import mock

from vincetools.compat import GzipFile

import vincetools.compat as vt_comp

from midas import RankEntry
from midas.tests import TEST_SITE_COUNT
from midas.tests import TEST_ALEXA_TOP1M
from midas.tests import TEST_ALEXA_TOP1M_FILES
from midas.tests import ConfiguredDBTestCase

class AlexaToKeyJobTests(vt_comp.unittest.TestCase):

    def _get_target_cls(self):
        from midas.scripts.alexa_to_key_files import AlexaToKeyJob
        return AlexaToKeyJob

    def test_mapper_on_test_data(self):
        j = self._get_target_cls()()
        result = []
        for alexa_f in TEST_ALEXA_TOP1M_FILES:
            result.extend(j.mapper(None, alexa_f))
        self.assertEqual(sorted(result),
                         sorted((e.key, [e.site, e.tstamp, e.rank])
                                for e in TEST_ALEXA_TOP1M))

    def test_reducer_on_test_data(self):
        a_date = datetime.date(1900, 1, 1)
        one_day = datetime.timedelta(days=1)
        foos = (RankEntry('foo', a_date, 2),
                RankEntry('foo', a_date + one_day, 1),
                RankEntry('foo', a_date + one_day*2, 1),
                RankEntry('foo', a_date + one_day*3, 1))
        bars = (RankEntry('bar', a_date, 2),
                RankEntry('bar', a_date + one_day, 1),
                RankEntry('bar', a_date + one_day*2, 1),
                RankEntry('bar', a_date + one_day*5, 1))
        in_foos = list(foos)
        random.shuffle(in_foos)
        in_bars = list(bars)
        random.shuffle(in_bars)
        tmpd = tempfile.mkdtemp()
        try:
            with mock.patch('midas.scripts.alexa_to_key_files.tempfile.mkdtemp') as mkdtemp:
                mkdtemp.return_value = tmpd
                with mock.patch('midas.scripts.alexa_to_key_files.shutil.rmtree') as rmtree:
                    ret_code = self._run_it('-q', '-d', tmpd, 
                                            *( e.format_w_key 
                                               for e in in_foos + in_bars ))
                    rmtree.assert_called_with(tmpd)
            self.assertEqual(ret_code, 0)
            listing = os.listdir(tmpd)
            listing.sort()
            # foo -> 0be; bar -> 62c
            self.assertEqual(listing, ['0be.gz', '62c.gz']) 
            with GzipFile(os.path.join(tmpd, '0be.gz')) as fp:
                self.assertEqual(fp.readlines(), 
                                 [ (l.format_std + '\n').encode()
                                   for l in foos ])
            with GzipFile(os.path.join(tmpd, '62c.gz')) as fp:
                self.assertEqual(fp.readlines(), 
                                 [ (l.format_std + '\n').encode()
                                   for l in bars ])
        finally:
            shutil.rmtree(tmpd)

class CheckTests(ConfiguredDBTestCase):

    def test_check_and_calc_stats(self):
        from midas.scripts.alexa_to_key_files \
            import check_and_calc_mean_max_min_deviation_variance
        result = check_and_calc_mean_max_min_deviation_variance()
        self.assertEqual(result, (1.5, 2, 1, .5, .25))

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
