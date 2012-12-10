# -*- coding: utf-8 -*-

#import mrjob.util as mr_util

import midas.compat as vt_comp

@vt_comp.unittest.skip('Is going to be removed')
class InvertIndexTests(vt_comp.unittest.TestCase):

    def _get_target_cls(self):
        from midas.scripts.invert_index import InvertIndex
        return InvertIndex

    def test_mapper(self):
        j = self._get_target_cls()()
        key, value = next(j.mapper(None, {'site': 'foo.example.com', 
                                          'rank': 1,
                                          'tstamp': '2012-11-17'}))
        self.assertEqual(key, 'foo.example.com')
        self.assertEqual(value, ('2012-11-17', 1))

    def test_reducer(self):
        j = self._get_target_cls()()
        key, value = next(j.reducer('foo.example.com', [('2012-11-18', 3),
                                                        ('2012-11-17', 2)]))
        self.assertEqual(key, 'foo.example.com')
        self.assertEqual(value, [('2012-11-17', 2), ('2012-11-18', 3)])

    def test_job(self):
        stdin = vt_comp.StringIO(
            '\n'.join([
                    '{"site": "foo.example.com", "rank": 2, "tstamp": "2012-11-17"}',
                    '{"site": "baz.bar.example.com/path", "rank": 1, "tstamp": "2012-11-17"}',
                    '{"site": "foo.example.com", "rank": 3, "tstamp": "2012-11-18"}',
                    '{"site": "baz.bar.example.com/path", "rank": 2, "tstamp": "2012-11-18"}',
                    ]) + '\n')
        j = self._get_target_cls()(['-r', 'inline', '--no-conf', '-'])
        j.sandbox(stdin=stdin)
        with j.make_runner() as runner:
            mr_util.log_to_null()
            runner.run()
            result = [ j.parse_output_line(line) 
                       for line in runner.stream_output() ]
        self.assertEqual(
            sorted(result),
            sorted(
                [("foo.example.com", [["2012-11-17", 2], ["2012-11-18", 3]]),
                 ("baz.bar.example.com/path", [["2012-11-17", 1], ["2012-11-18", 2]])]
                )
            )
