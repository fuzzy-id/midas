# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import datetime
import hashlib
import os
import os.path
import sys

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from midas import RankEntry
from midas.compat import GzipFile

Base = declarative_base()
Session = sessionmaker()

def run_alexa_to_sha1(argv=sys.argv):
    cmd = AlexaToSha1(argv)
    return cmd.run()

class AlexaToSha1(object):
    """ Parse Alexa Top1M files and print the found entries in key
    format. When no file is, given the names of the files are read
    from stdin.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-q', '--quiet', action='store_true', default=False,
                        help='do not print status messages')
    parser.add_argument('stream', nargs='*', metavar='FILE', default=sys.stdin)

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

def sort_sha1(argv=sys.argv):
    """ Sort entries provided in key format in descending order. Put
    them in standard format in a gzipped file named after the key.
    """
    descr = ' '.join(('Parse entries in key format, sort them and print',
                      'them in standard format in a gzipped file named',
                      'like the key.'))
    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument('-q', '--quiet', action='store_true', default=False,
                        help='do not print status messages')
    parser.add_argument('stream', nargs='*', metavar='ENTRY', default=sys.stdin,
                        help=' '.join(('the entries to process, when no entry',
                                       'is given the entries are read from',
                                       'stdin')))
    args = parser.parse_args(argv[1:])
    for line in args.stream:
        entry = RankEntry.parse_std(line)
        print("Processing '{0}'".format(fname))
        with open(fname) as fp:
            if os.fstat(fp.fileno()).st_size == 0:
                print('File is empty. Skipping.')
                continue
            sha_start, _ = next(fp).split('\t')
            sha_fname = '{0}.gz'.format(sha_start)
            assert not os.path.exists(sha_fname)
            fp.seek(0)
            lines = []
            for l in fp:
                l = l.strip()
                name, ts, rank = l.split('\t')[1].split(', ')
                lines.append((name, ts, rank))
        lines.sort()
        print("Writing to '{0}'".format(sha_fname))
        with GzipFile(sha_fname, 'wb') as sha_fp:
            for entry in lines:
                sha_fp.write('{0}\t{1}, {2}\n'.format(entry[0], entry[1], entry[2]))
    return 0
        

class Rank(Base):
    __tablename__ = 'ranking'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    rank = Column(Integer)
    ts = Column(DateTime)


def push_to_db():
    db = sys.argv[1]
    print("Working on '{0}'".format(db))
    engine = create_engine(db)
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    for fname in sys.stdin:
        fname = fname.strip()
        print("Processing '{0}'".format(fname), file=sys.stderr)
        date = convert_fname_to_date(fname)
        for l in unzip_file(fname):
            rank, name = split_rank_name(l)
            entry = Rank(name=name, rank=rank, ts=date)
            session.add(entry)
        else:
            session.commit()
            print("Commited", file=sys.stderr)
    return 0
