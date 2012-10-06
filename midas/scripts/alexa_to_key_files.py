# -*- coding: utf-8 -*-

from __future__ import print_function

import collections
import logging
import os.path
import shutil
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
