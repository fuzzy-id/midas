# -*- coding: utf-8 -*-

import datetime
import os.path
import tempfile

import mock

from vincetools.compat import StringIO
from vincetools.compat import unittest

class MDLaunchTests(unittest.TestCase):

    config = ['[hadoop]',
              'exec = echo',
              'streaming = a_stream',
              '[job]']

    def setUp(self):
        import midas.config as md_cfg
        md_cfg.new_configparser()

    def _get_target_cls(self):
        from midas.scripts.md_launch import MDLaunch
        return MDLaunch

    def _call_cmd(self, *args):
        effargs = ['md_launch']
        effargs.extend(args)
        return self._get_target_cls().cmd(effargs)

    def test_output_is_generated_by_default(self):
        with tempfile.NamedTemporaryFile('w+') as fp:
            fp.writelines('\n'.join(self.config))
            fp.seek(0)
            mdl = self._get_target_cls()(['md_launch', fp.name])
        out_dst = mdl.proc_cmd[mdl.proc_cmd.index('-output') + 1]
        self.assertIn(os.path.basename('_{0}_'.format(fp.name)), out_dst)
        self.assertIn(datetime.date.today().strftime('_%Y-%m-%d_'), out_dst)
            
    @mock.patch('midas.tools.logger')
    def test_echo_line_to_stdout(self, logger):
        with tempfile.NamedTemporaryFile('w+') as fp:
            fp.writelines('\n'.join(self.config + ['mapper = foo',
                                                   'num_mappers = 1',
                                                   'reducer = bar',
                                                   'num_reducers = 10',
                                                   'compress_output = false',
                                                   'input = input_file',
                                                   'output = out']))
            fp.seek(0)
            self.assertEqual(0, self._call_cmd(fp.name))
        self.assertFalse(logger.error.called)
        self.assertTrue(logger.info.called)
        expected = ' '.join(('jar', 'a_stream', 
                             '-D mapred.map.tasks=1', 
                             '-D mapred.reduce.tasks=10', 
                             '-mapper foo -reducer bar', 
                             '-input input_file -output out'))
        logger.info.assert_called_with(expected)
        logger.info.assert_any_call("Executing 'echo {0}'".format(expected))
