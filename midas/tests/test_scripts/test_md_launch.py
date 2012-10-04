# -*- coding: utf-8 -*-

from midas.compat import StringIO
from midas.tests import IntegrationTestCase

class MDLaunchTests(IntegrationTestCase):

    def _call_cmd(self, *args):
        effargs = ['md_launch']
        effargs.extend(args)
        from midas.scripts.md_launch import MDLaunch
        return MDLaunch.cmd(effargs)

    def test_subproc_writes_to_stdout(self):
        cfg = StringIO('\n'.join(('[hadoop]',
                                  'exec = echo',
                                  '[job]',
                                  'mapper = foo',
                                  'reducer = bar')))
        cfg.seek(0)
        self.assertEqual(0, self._call_cmd(cfg))
        self.assert_stdout_startswith('jar')
        
