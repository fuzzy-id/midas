# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import datetime
import hashlib
import logging
import os
import os.path
import shutil
import subprocess
import sys
import tempfile

from midas import MDCommand
from midas import RankEntry
from midas.compat import GzipFile

logger = logging.getLogger(__name__)


def popen_log(cmd):
    logging.info("Executing '{0}'".format(' '.join(cmd)))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    if proc.returncode != 0:
        logging.critical('STDOUT: {0}\nSTDERR: {1}'.format(*proc.communicate()))
        raise subprocess.CalledProcessError(proc.returncode, cmd)
    else:
        proc.stdout.close()
        proc.stderr.close()


def get_hadoop_binary():
    return os.path.join(os.environ['HADOOP_HOME'], 'bin', 'hadoop')


class AlexaToKey(MDCommand):
    """ Parse Alexa Top1M files and print the found entries in key
    format. When no file is given the names of the files are read from
    stdin.
    """

    def run(self):
        for fname in self.args.stream:
            fname = fname.strip()
            logging.info("processing '{0}'".format(fname))
            for entry in RankEntry.iter_alexa_file(fname):
                print(entry.format_w_key)
        return 0


class KeyToFiles(MDCommand):
    """ Sort entries provided in key format in descending order. Put
    them in standard format in a gzipped file named after the
    key. When no entry is given the entries are read from stdin.
    """

    def __init__(self, argv=sys.argv):
        MDCommand.__init__(self, argv)
        self.tmp_files = []
        self.tmpd = None
        self.cache = []

    def run(self):
        logging.basicConfig(level=self.args.verbosity, stream=sys.stderr)
        stream_iter = iter(self.args.stream)
        first = next(stream_iter)
        self.cache.append(RankEntry.parse_key(first))
        self.tmpd = tempfile.mkdtemp()
        try:
            for line in stream_iter:
                entry = RankEntry.parse_key(line)
                if entry.key != self.cache[0].key:
                    self._write_out_cache()
                    self._cp_tmp_files_to_hdfs()
                self.cache.append(entry)
            else:
                self._write_out_cache()
            self._cp_tmp_files_to_hdfs()
        finally:
            shutil.rmtree(self.tmpd)
        return 0

    def add_argument(self):
        self.parser.add_argument('-d', '--dest', default='.',
                                 help='destination for the output files')


    def _write_out_cache(self):
        self.cache.sort()
        tmpfile = os.path.join(self.tmpd, '{0}.gz'.format(self.cache[0].key))
        logging.info('Writing to {0}'.format(tmpfile))
        with GzipFile(tmpfile, 'wb') as fp:
            for entry in self.cache:
                fp.write((entry.format_std + '\n').encode())
        self.tmp_files.append(tmpfile)
        self.cache = []
        logging.info('Generated {0}'.format(tmpfile))

    def _cp_tmp_files_to_hdfs(self):
        copied = []
        try:
            for tmpfile in self.tmp_files:
                dst_file = os.path.join(self.args.dest, os.path.basename(tmpfile))
                cmd = (get_hadoop_binary(), 'fs', '-put', tmpfile, dst_file)
                popen_log(cmd)
                copied.append(dst_file)
        except:
            logging.critical('Removing copied files from HDFS.')
            for dst_file in copied:
                cmd = (get_hadoop_binary(), 'fs', '-rm', dst_file)
                popen_log(cmd)
            raise
