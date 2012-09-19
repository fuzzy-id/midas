# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from midas.mapper import convert_fname_to_date
from midas.mapper import split_rank_name
from midas.mapper import unzip_file


Base = declarative_base()
Session = sessionmaker()

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
