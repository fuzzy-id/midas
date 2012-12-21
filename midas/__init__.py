# -*- coding: utf-8 -*-
""" Common functions that are needed in most other submodules.
"""

import datetime
import json
import os.path

import midas.compat as vt_comp

#: The standard format we use to produce and parse time-stamps.
TS_FORMAT = '%Y-%m-%d'

def parse_tstamp(s, fmt=TS_FORMAT):
    return datetime.datetime.strptime(s, fmt)

def serialize_tstamp(tstamp, fmt=TS_FORMAT):
    return tstamp.strftime(fmt)

class RankEntry(object):
    """ Return an entry of a ranking for `site`.

    The `date` specifies the date of the entry and should be a
    :class:`datetime.datetime` instance.

    The `rank` is expected to be an integer.

    Methods are provided both, to format a :class:`RankEntry` in
    standardized manners and to parse these formats back.
    """ 

    def __init__(self, site, date, rank):
        self.site = site
        self.date = date
        self.rank = rank
        self._key = None

    def __str__(self):
        return 'RankEntry({e.site}, {e.tstamp}, {e.rank})'.format(e=self)

    def __eq__(self, other):
        return (self.site == other.site
                and self.date == other.date
                and self.rank == other.rank)

    def __lt__(self, other):
        if self.site < other.site:
            return True
        elif self.site > other.site:
            return False
        elif self.date < other.date:
            return True
        elif self.date > other.date:
            return False
        elif self.rank < other.rank:
            return True
        else:
            return False

    def __le__(self, other):
        return self == other or self < other

    def __ge__(self, other):
        return not self < other

    def __gt__(self, other):
        return not self <= other

    @property
    def tstamp(self):
        " Return the `date` formated as defined in :attr:`TS_FORMAT`. "
        return self.date.strftime(TS_FORMAT)

    @property
    def format_json(self):
        """ Return the ``name``, ``rank`` and ``tstamp`` as dictionary
        in JSON representation.
        """
        return json.dumps({'site': self.site,
                           'rank': self.rank,
                           'tstamp': self.tstamp})

    @classmethod
    def parse_json(cls, s):
        " Parse back :meth:`RankEntry.format_json`. "
        d = json.loads(s)
        date = parse_tstamp(d['tstamp'])
        return cls(site=d['site'], date=date, rank=d['rank'])

    @classmethod
    def iter_alexa_file(cls, fname):
        """ Returns an iterator yielding a :class:`RankEntry` for
        every line it finds in the file in the archive `fname`.

        The standard Alexa Top1M data is a
        :class:`zipfile.ZipFile`. The archive contains one file named
        `top-1m.csv`. The lines in this file have the form
        `rank,site_name` (no spaces!).

        As the time-stamp is encoded in the file name (defined by
        :attr:`ALEXA_TS_FORMAT`) and not in the line, parsing cannot be
        done line-by-line but needs to be done on a per file basis.
        """
        fname = fname.strip()
        fname_last = os.path.basename(fname)
        date = parse_tstamp(fname_last, ALEXA_TS_FORMAT)
        with vt_comp.ZipFile(fname) as zf:
            # The archive contains one file named ``top-1m.csv``
            for line in zf.open('top-1m.csv'):
                rank, name = line.decode().strip().split(',', 1)
                yield cls(name, date, int(rank))
