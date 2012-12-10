# -*- coding: utf-8 -*-

import tempfile

import midas.compat as vt_comp

import midas.tests.test_scripts as md_test_scripts
import midas.config as md_cfg

class IndexDatesTests(md_test_scripts.IntegrationTestCaseNG):

    def _get_target_cls(self):
        from midas.scripts.index_dates import IndexDates
        return IndexDates

    def test_on_test_data(self):
        with tempfile.NamedTemporaryFile() as tmp_f:
            md_cfg.set('location', 'dates_file', tmp_f.name)
            self.assertEqual(self._call_cmd(), 0)
            with vt_comp.GzipFile(tmp_f.name) as fp:
                result = [ l.decode().strip() for l in fp ]
        self.assertEqual(result, ['2012-09-03', '2012-09-04'])


if __name__ == '__main__':  # pragma: no cover
    vt_comp.unittest.main()
