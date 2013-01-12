# -*- coding: utf-8 -*-

from midas.tests import TEST_DATA_PATH
from midas.tests.test_scripts import MDCommandTestCase

class MakeTstampToSecsTests(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts.tstamp_to_secs import TstampToSecs
        return TstampToSecs

    def test_on_test_data(self):
        self._call_cmd(TEST_DATA_PATH['alexa_files'])
        self.assert_stdout_equal('\n'.join(['2012-09-03\t1346623200',
                                            '2012-09-04\t1346709600',
                                            '']))
