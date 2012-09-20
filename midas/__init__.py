# -*- coding: utf-8 -*-
""" Common functions that are needed in most other submodules.
"""

import datetime
import hashlib
import os.path

from midas.compat import ZipFile

#: How much letters of the hash key should be used to pre-sort the
#: entries. The larger this number the more and smaller files
#: will be produced. The default value is `2` which gives us `16 * 16 =
#: 256` files.
CUT_HASH_KEY = 2

class RankEntry(object):
    """ Returns an entry of a ranking for `site`.

    The `date` specifies the date of the entry and should be a
    :class:`datetime.datetime` instance.

    The `rank` is expected to be an integer.

    Methods are provided both, to format a :class:`RankEntry` in
    standardized manners and to parse these formats back.
    """ 
    #: The standard format we use to produce and parse time-stamps.
    TS_FORMAT = '%Y-%m-%d'
    #: The time-stamp format as encoded in Alexa's Top1M files.
    ALEXA_TS_FORMAT = 'top-1m-%Y-%m-%d.csv.zip'

    def __init__(self, name, date, rank):
        self.name = name
        self.date = date
        self.rank = rank
        self._key = None

    def __str__(self):
        return 'RankEntry({e.name}, {e.date}, {e.rank})'.format(e=self)

    def __lt__(self, other):
        return (self.name < other.name 
                and self.date < other.date
                and self.rank < other.rank)

    def __le__(self, other):
        return (self.name <= other.name 
                and self.date <= other.date
                and self.rank <= other.rank)
        
    def __eq__(self, other):
        return (self.name == other.name
                and self.date == other.date
                and self.rank == other.rank)

    @property
    def format_std(self):
        " `'name[TAB]tstamp,[SPACE]rank'`. "
        return '{e.name}\t{e.tstamp}, {e.rank}'.format(e=self)

    @property
    def tstamp(self):
        " The `date` formated as defined in :attr:`TS_FORMAT`. "
        return datetime.datetime.strftime(self.date, self.TS_FORMAT)

    @property
    def format_w_key(self):
        " `'key[TAB]format_std'` "
        return '{e.key}\t{e.format_std}'.format(e=self)

    @property
    def key(self):
        """ The first :attr:`CUT_HASH_KEY` digits of the hash produced
        by :func:`hashlib.sha1` on the `name`. The key is computed and
        cached even though the `name` changes.
        """
        if self._key is None:
            self._key = hashlib.sha1(self.name.encode()).hexdigest()[:CUT_HASH_KEY]
        return self._key

    @classmethod
    def parse_std(self, s):
        pass
        
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
        date = datetime.datetime.strptime(fname_last, cls.ALEXA_TS_FORMAT)
        with ZipFile(fname) as zf:
            # The archive contains one file named ``top-1m.csv``
            for line in zf.open('top-1m.csv'):
                rank, name = line.decode().strip().split(',', 1)
                yield cls(name, date, int(rank))
