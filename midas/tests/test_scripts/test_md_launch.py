# -*- coding: utf-8 -*-

import tempfile

import mock

from midas.compat import StringIO
from midas.tests import IntegrationTestCase

class MDLaunchTests(IntegrationTestCase):

    def _call_cmd(self, *args):
        effargs = ['md_launch']
        effargs.extend(args)
        from midas.scripts.md_launch import MDLaunch
        return MDLaunch.cmd(effargs)

    @mock.patch('midas.scripts.md_launch.logger')
    def test_subproc_stdout(self, logger):
        with tempfile.NamedTemporaryFile('w+') as fp:
            fp.writelines('\n'.join(('[hadoop]',
                                     'exec = echo',
                                     '[job]',
                                     'mapper = foo',
                                     'reducer = bar')))
            fp.seek(0)
            self.assertEqual(0, self._call_cmd(fp.name))
        self.assertFalse(logger.error.called)
        self.assertTrue(logger.info.called)
