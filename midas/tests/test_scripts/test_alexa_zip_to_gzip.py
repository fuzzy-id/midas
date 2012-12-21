# -*- coding: utf-8 -*-

import shutil
import os
import os.path
import tempfile

from midas.tests.test_scripts import IntegrationTestCaseNG
from midas.tests import TEST_DATA_PATH


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
        ret_code = self._call_cmd(TEST_DATA_PATH['alexa_zip_files'],
                                  self.tmpd)
        self.assertEqual(ret_code, 0)
        results = sorted(os.listdir(self.tmpd))
        expected = sorted(os.listdir(TEST_DATA_PATH['alexa_files']))
        self.assertEqual(results, expected)
        for fname in results:
            res = os.path.join(self.tmpd, fname)
            exp = os.path.join(TEST_DATA_PATH['alexa_files'], fname)
            with open(res) as fp1, open(exp) as fp2:
                for entry1, entry2 in zip(fp1, fp2):
                    self.assertEqual(entry1, entry2)

    def test_skip_already_present_files(self):
        first = os.path.join(self.tmpd, 'top_1m_2012-09-03')
        snd = os.path.join(self.tmpd, 'top_1m_2012-09-04')
        with open(first, 'w'), open(snd, 'w'):
            pass
        self.assertEqual(self._call_cmd(TEST_DATA_PATH['alexa_zip_files'], 
                                        self.tmpd), 0)
        with open(first) as fp:
            self.assertEqual(fp.readlines(), [])
        with open(snd) as fp:
            self.assertEqual(fp.readlines(), [])
        self.assert_in_cls_out('Skipping top-1m-2012-09-03.csv.zip\n')
        self.assert_in_cls_out('Skipping top-1m-2012-09-04.csv.zip\n')

if __name__ == '__main__':  # pragma: no cover
    from midas.compat import unittest
    unittest.main()
