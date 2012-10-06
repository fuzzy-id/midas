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

from midas import RankEntry
from midas.compat import GzipFile
from midas.compat import imap
from midas.scripts import MDJob
from midas.tools import group_by_key
from midas.tools import log_popen

import midas.hdfs as md_hdfs

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
            md_hdfs.put(files, self.args.dest)
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
