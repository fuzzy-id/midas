# -*- coding: utf-8 -*-

import shutil
import os.path
import tempfile

import vincetools.compat as vt_comp

from midas.tests.test_scripts import IntegrationTestCaseNG

import midas
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
