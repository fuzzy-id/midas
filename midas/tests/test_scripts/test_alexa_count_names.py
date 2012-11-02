# -*- coding: utf-8 -*-

import vincetools.compat as vt_comp

from midas.tests import TEST_ALEXA_TOP1M
from midas.tests import TEST_ALEXA_TOP1M_FILES

class AlexaCountSitesJobTests(vt_comp.unittest.TestCase):

    def _get_target_cls(self):
        from midas.scripts.alexa_count_sites import AlexaCountSitesJob
        return AlexaCountSitesJob

    def test_mapper_on_test_data(self):
        j = self._get_target_cls()()
        result = list()
        for alexa_f in TEST_ALEXA_TOP1M_FILES:
            result.extend(j.mapper(None, alexa_f))
        self.assertEqual(sorted(result), 
                         sorted((e.site, 1) for e in TEST_ALEXA_TOP1M))

    def test_reducer_simple(self):
        j = self._get_target_cls()()
        result = j.reducer('foo', range(4))
        self.assertEqual(next(result), ('foo', 6))

    def test_job(self):
        stdin = vt_comp.StringIO('\n'.join(TEST_ALEXA_TOP1M_FILES) + '\n')
        j = self._get_target_cls()(['--no-conf', '-r', 'inline', '-'])
        j.sandbox(stdin=stdin)
        with j.make_runner() as runner:
            runner.run()
            result = [ line for line in runner.stream_output() ]
        self.assertEqual(sorted(result), [ '"baz.bar.example.com/path"\t2\n',
                                           '"foo.example.com"\t1\n' ])
        
