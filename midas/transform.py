# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import collections
import datetime
import hashlib
import logging
import os
import os.path
import shutil
import subprocess
import sys
import tempfile

from midas import MDJob
from midas import RankEntry
from midas.analyze import group_by_key
from midas.compat import GzipFile
from midas.compat import imap
from midas.tools import log_popen


logger = logging.getLogger(__name__)

def get_hadoop_binary():
    return os.path.join(os.environ['HADOOP_HOME'], 'bin', 'hadoop')


class AlexaToKey(MDJob):
    """ Parse Alexa Top1M files and print the found entries in key
    format. When no file is given the names of the files are read from
    stdin.
    """

    def run(self):
        for fname in self.args.stream:
            fname = fname.strip()
            logger.info("processing '{0}'".format(fname))
            for entry in RankEntry.iter_alexa_file(fname):
                print(entry.format_w_key)
        return 0


class KeyToFiles(MDJob):
    """ Sort entries provided in key format in descending order. Put
    them in standard format in a gzipped file named after the
    key. When no entry is given the entries are read from stdin.
    """

    def __init__(self, argv=sys.argv):
        MDJob.__init__(self, argv)
        self.tmp_files = []
        self.tmpd = None

    def run(self):
        self.tmpd = tempfile.mkdtemp()
        try:
            files = [ self._write_out(sorted(imap(RankEntry.parse_key, group)))
                      for group in group_by_key(self.args.stream) ]
            self._cp_files_to_hdfs(files)
        finally:
            shutil.rmtree(self.tmpd)
        return 0

    def add_argument(self):
        self.parser.add_argument('-d', '--dest', default='.',
                                 help='destination for the output files')

    def _write_out(self, cache):
        tmpfile = os.path.join(self.tmpd, '{0}.gz'.format(cache[0].key))
        logger.info('Writing to {0}'.format(tmpfile))
        with GzipFile(tmpfile, 'wb') as fp:
            for entry in cache:
                fp.write((entry.format_std + '\n').encode())
        logger.info('Generated {0}'.format(tmpfile))
        return tmpfile

    def _cp_files_to_hdfs(self, files):
        copied = []
        try:
            for tmpfile in files:
                dst_file = os.path.join(self.args.dest, 
                                        os.path.basename(tmpfile))
                cmd = (get_hadoop_binary(), 'fs', '-put', tmpfile, dst_file)
                log_popen(cmd)
                copied.append(dst_file)
        except:
            logger.critical('Removing copied files from HDFS.')
            for dst_file in copied:
                cmd = (get_hadoop_binary(), 'fs', '-rm', dst_file)
                log_popen(cmd)
            raise

def entries_cnt(files):
    counter = collections.defaultdict(int)
    for f in files:
        f_name = os.path.basename(f)
        f_sha = f_name[:3]
        with GzipFile(f) as fp:
            print("Processing {0}".format(f_sha))
            for line in fp:
                entry = RankEntry.parse_std(line.decode())
                if entry.key != f_sha:
                    raise Exception('{0} != {1}'.format(entry.key, f_sha))
                counter[f_sha] += 1
    return counter
