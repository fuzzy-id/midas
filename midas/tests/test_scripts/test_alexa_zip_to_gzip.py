# -*- coding: utf-8 -*-

import shutil
import os.path
import tempfile

import midas.compat as vt_comp

from midas.tests.test_scripts import IntegrationTestCaseNG

import midas
import midas.config as md_cfg
import midas.tests as md_tests

class AlexaZipToGzipTests(IntegrationTestCaseNG):

    def setUp(self):
        super(AlexaZipToGzipTests, self).setUp()
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)
        super(AlexaZipToGzipTests, self).tearDown()

    def _get_target_cls(self):
        from midas.scripts.alexa_zip_to_gzip import AlexaZipToGzip
        return AlexaZipToGzip

    def test_on_test_data(self):
        ret_code = self._call_cmd(
            os.path.dirname(md_tests.TEST_ALEXA_TOP1M_FILES[0]),
            self.tmpd
            )
        self.assertEqual(ret_code, 0)
        first = os.path.join(self.tmpd, 'top_1m_2012-09-03.gz')
        snd = os.path.join(self.tmpd, 'top_1m_2012-09-04.gz')
        self.assertTrue(os.path.isfile(first))
        self.assertTrue(os.path.isfile(snd))
        with vt_comp.GzipFile(first) as fp:
            entries = [ midas.RankEntry.parse_json(l.decode('utf-8'))
                        for l in fp ]
        self.assertEqual(entries, md_tests.TEST_ALEXA_TOP1M[:2])
        with vt_comp.GzipFile(snd) as fp:
            entries = [ midas.RankEntry.parse_json(l.decode('utf-8'))
                        for l in fp ]
        self.assertEqual(entries, md_tests.TEST_ALEXA_TOP1M[2:])

    def test_skip_already_present_files(self):
        md_cfg.set('location', 'alexa_files', self.tmpd)
        first = os.path.join(self.tmpd, 'top_1m_2012-09-03.gz')
        snd = os.path.join(self.tmpd, 'top_1m_2012-09-04.gz')
        with open(first, 'w'):
            pass
        with open(snd, 'w'):
            pass
        self.assertEqual(self._call_cmd(), 0)
        with open(first) as fp:
            self.assertEqual(fp.readlines(), [])
        with open(snd) as fp:
            self.assertEqual(fp.readlines(), [])
        self.assert_in_cls_out('top-1m-2012-09-03.csv.zip SKIP\n')
        self.assert_in_cls_out('top-1m-2012-09-04.csv.zip SKIP\n')

if __name__ == '__main__':  # pragma: no cover
    vt_comp.unittest.main()
