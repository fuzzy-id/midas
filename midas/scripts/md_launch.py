# -*- coding: utf-8 -*-

import logging
import os
import os.path
import subprocess

from midas import MDCommand

logger = logging.getLogger(__name__)

def which(program):
   def is_exe(fpath):
      return (not os.path.isdir(fpath) 
              and os.path.exists(fpath) 
              and os.access(fpath, os.F_OK | os.X_OK))
   if is_exe(program):
       return program
   for path in os.environ["PATH"].split(os.pathsep):
       exe_file = os.path.join(path, program)
       if is_exe(exe_file):
           return exe_file
   return None


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

    def run(self):
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
       proc_cmd.extend(
          ['-files', self.config.get('alexa', 'top1m_files'),
           '-input', self.config.get('job', 'input'),
           '-output', self.config.get('job', 'output'),
           '-mapper', self.config.get('job', 'mapper'),
           '-reducer', self.config.get('job', 'reducer')])
       logger.info("Executing '{0}'".format(' '.join(proc_cmd)))
       proc = subprocess.Popen(proc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       while proc.poll() is None:
          for l in proc.stderr:
             logger.error(l.strip())
          for l in proc.stdout:
             logger.info(l.strip())
       else:
          for l in proc.stderr:
             logger.error(l.strip())
          proc.stderr.close()
          for l in proc.stdout:
             logger.info(l.strip())
          proc.stdout.close()
       return proc.poll()
          
