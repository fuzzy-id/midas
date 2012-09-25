# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import datetime
import hashlib
import os
import os.path
import shutil
import subprocess
import sys
import tempfile

from midas import RankEntry
from midas.compat import GzipFile

def run_alexa_to_key(argv=sys.argv):
    cmd = AlexaToKey(argv)
    return cmd.run()

class AlexaToKey(object):
    """ Parse Alexa Top1M files and print the found entries in key
    format. When no file is given the names of the files are read from
    stdin.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-q', '--quiet', action='store_true', default=False,
                        help='do not print status messages')
    parser.add_argument('stream', nargs='*', metavar='FILE', default=sys.stdin,
                        help='the files to read')

    def __init__(self, argv):
        self.args = self.parser.parse_args(argv[1:])

    def run(self):
        for fname in self.args.stream:
            fname = fname.strip()
            if not self.args.quiet:  # pragma: no cover
                print("processing '{0}'".format(fname), file=sys.stderr)
            for entry in RankEntry.iter_alexa_file(fname):
                print(entry.format_w_key)
        return 0

def run_key_to_files(argv=sys.argv):
    cmd = KeyToFiles(argv)
    return cmd.run()

class KeyToFiles(object):
    """ Sort entries provided in key format in descending order. Put
    them in standard format in a gzipped file named after the
    key. When no entry is given the entries are read from stdin.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-q', '--quiet', action='store_true', default=False,
                        help='do not print status messages')
    parser.add_argument('-d', '--dest', default='.',
                        help='destination for the output files')
    parser.add_argument('stream', nargs='*', metavar='ENTRY', default=sys.stdin,
                        help='the entries to process, ')

    def __init__(self, argv):
        self.args = self.parser.parse_args(argv[1:])

    def run(self):
        stream_iter = iter(self.args.stream)
        first = next(stream_iter)
        cache = [RankEntry.parse_key(first)]
        for line in stream_iter:
            entry = RankEntry.parse_key(line)
            if entry.key != cache[0].key:
                self._write_out(cache)
                cache = []
            cache.append(entry)
        else:
            self._write_out(cache)
        return 0

    def _write_out(self, entries):
        entries.sort()
        tmpd = tempfile.mkdtemp()
        try:
            key_file = '{0}.gz'.format(entries[0].key)
            tmpfile = os.path.join(tmpd, key_file)
            with GzipFile(tmpfile, 'wb') as fp:
                for entry in entries:
                    fp.write((entry.format_std + '\n').encode())
            dst_file = os.path.join(self.args.dest, key_file)
            cmd = (get_hadoop_binary(), 'fs', '-put', tmpfile, dst_file)
            if not self.args.quiet:
                print("Executing '{0}'".format(' '.join(cmd)), file=sys.stderr)
            try:
                proc = subprocess.Popen(cmd, 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
                proc.wait()
                if proc.returncode != 0:
                    print('STDOUT: {0}\nSTDERR: {1}'.format(*proc.communicate()),
                          file=sys.stderr)
                    raise subprocess.CalledProcessError(proc.returncode, cmd)
            except OSError as e:
                print(sys.exc_info(), file=sys.stderr)
                raise
        finally:
            shutil.rmtree(tmpd)

def get_hadoop_binary():
    return os.path.join(os.environ['HADOOP_HOME'], 'bin', 'hadoop')
