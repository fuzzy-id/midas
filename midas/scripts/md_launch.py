# -*- coding: utf-8 -*-

import datetime
import logging
import os
import os.path
import subprocess

from midas.tools import log_popen
from midas import MDCommand

logger = logging.getLogger(__name__)


class MDLaunch(MDCommand):
    """ Launches a MapReduce job defined by the passed job
    configuration file.
    """

    POS_ARG = {'dest': 'job_cfg',
               'nargs': 1,
               'metavar': 'FILE',
               'help': 'the configuration of the job'}

    def __init__(self, argv):
       MDCommand.__init__(self, argv)
       self.config.read(self.args.job_cfg)
       proc_cmd = [self.config.get('hadoop', 'exec'), 
                   'jar', self.config.get('hadoop', 'streaming')]
       proc_cmd.extend(
          ['-D', "mapred.map.tasks={0}".format(self.config.getint('job', 'num_mappers'))])
       proc_cmd.extend(
          ['-D', "mapred.reduce.tasks={0}".format(self.config.getint('job', 'num_reducers'))])
       if self.config.getboolean('job', 'compress_output'):
          proc_cmd.extend(
             ['-D', 'mapred.output.compress=true',
              '-D', 'mapred.output.compression.codec=org.apache.hadoop.io.compress.GzipCodec'])

       if self.config.get('job', 'output') == 'optional':
          out_dst = 'out_{0}_%Y-%m-%d_%H-%M-%S'.format(self.args.job_cfg[0])
          out_dst = datetime.datetime.now().strftime(out_dst)
          self.config.set('job', 'output', out_dst)
          logger.info("Output goes to '{0}'".format(out_dst))

       for field in ('files', 'mapper', 'reducer', 'input', 'output'):
          if self.config.get('job', field) != 'optional':
             proc_cmd.append('-{0}'.format(field))
             proc_cmd.append(self.config.get('job', field))
       self.proc_cmd = proc_cmd

    def run(self):
       return log_popen(self.proc_cmd)

