# -*- coding: utf-8 -*-

import tempfile

import mock

from midas.compat import StringIO
from midas.tests import unittest

class MDLaunchTests(unittest.TestCase):

    def _call_cmd(self, *args):
        effargs = ['md_launch']
        effargs.extend(args)
        from midas.scripts.md_launch import MDLaunch
        return MDLaunch.cmd(effargs)

    @mock.patch('midas.scripts.md_launch.logger')
    def test_echo_line_to_stdout(self, logger):
        with tempfile.NamedTemporaryFile('w+') as fp:
            fp.writelines('\n'.join(('[hadoop]',
                                     'exec = echo',
                                     'streaming = a_stream',
                                     '[job]',
                                     'mapper = foo',
                                     'num_mappers = 1',
                                     'reducer = bar',
                                     'num_reducers = 10',
                                     'compress_output = false',
                                     'input = input_file',
                                     'output = out')))
            fp.seek(0)
            self.assertEqual(0, self._call_cmd(fp.name))
        self.assertFalse(logger.error.called)
        self.assertTrue(logger.info.called)
        expected = ' '.join(('jar', 'a_stream', '-D mapred.map.tasks=1', 
                             '-D mapred.reduce.tasks=10', '-input input_file',
                             '-output out -mapper foo -reducer bar'))
        logger.info.assert_called_with(expected)
        logger.info.assert_any_call("Executing 'echo {0}'".format(expected))

