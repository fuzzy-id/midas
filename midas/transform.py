# -*- coding: utf-8 -*-

from __future__ import print_function

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

from midas import Entry
from midas.compat import GzipFile

Base = declarative_base()
Session = sessionmaker()

def mapper():
    for fname in sys.stdin:
        fname = fname.strip()
        print("Processing '{0}'".format(fname), file=sys.stderr)
        for entry in Entry.iter_alexa_file(fname):
            rank, name = split_rank_name(l)
            h = hashlib.sha1(name).hexdigest()
            h_start = h[:2]
            print("{0}\t{1}, {2}, {3}".format(h_start, name, tstamp, rank))
    return 0

def sort_sha1():
    for fname in sys.argv[1:]:
        fname = fname.strip()
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
