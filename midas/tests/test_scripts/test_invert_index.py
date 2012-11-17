# -*- coding: utf-8 -*-

import vincetools.compat as vt_comp

class InvertIndexTests(vt_comp.unittest.TestCase):

    def _get_target_cls(self):
        from midas.scripts.invert_index import InvertIndex
        return InvertIndex

    def test_mapper(self):
        j = self._get_target_cls()()
        key, value = j.mapper(None, {'site': 'foo.example.com', 
                                     'rank': 1,
                                     'tstamp': '2012-11-17'})
        self.assertEqual(key, 'foo.example.com')
        self.assertEqual(value, ('2012-11-17', 1))

    def test_job(self):
        j = self._get_target_cls()(['-r', 'inline', '--no-conf', '-'])
        
