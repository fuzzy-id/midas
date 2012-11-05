# -*- coding: utf-8 -*-
""" Common functions that are needed in most other submodules.
"""

import datetime
import hashlib
import json
import logging
import os.path

from vincetools.compat import ZipFile
import vincetools.compat as vt_comp

import midas.config as md_cfg
import midas.tools as md_tools

logger = logging.getLogger(__name__)

class RankEntry(object):
    """ Return an entry of a ranking for `site`.

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
    def format_std(self):
        " `'site[TAB]tstamp,[SPACE]rank'`. "
        return '{e.site}\t{e.tstamp}, {e.rank}'.format(e=self)

    @property
    def tstamp(self):
        " Return the `date` formated as defined in :attr:`TS_FORMAT`. "
        return self.date.strftime(self.TS_FORMAT)

    @property
    def format_w_key(self):
        " `'key[TAB]format_std'` "
        return '{e.key}\t{e.format_std}'.format(e=self)

    @property
    def format_json(self):
        """ Return the ``name``, ``rank`` and ``tstamp`` as dictionary
        in JSON representation.
        """
        return json.dumps({'site': self.site,
                           'rank': self.rank,
                           'tstamp': self.tstamp})

    @property
    def key(self):
        """ The cached key as computed by
        :meth:`RankEntry.make_key`. Note that the key is cached: even
        though `self.site` changes `self.key` will remain the
        same. You can force a recomputation of the key by setting
        `self.key` to :const:`None`.
        """
        if self._key is None:
            self._key = self.make_key(self.site)
        return self._key

    @classmethod
    def make_key(cls, s):
        """ The first :attr:`midas.config.get('alexa', 'key_length')`
        digits of the hash produced by :func:`hashlib.sha1` on the
        `site`. 
        """
        domain = md_tools.domain(s)
        sha1 = hashlib.sha1(domain.encode()).hexdigest()
        return sha1[:md_cfg.getint('location', 'key_length')]

    @classmethod
    def parse_key(cls, s):
        " Parse back :meth:`RankEntry.format_key`. "
        key, std = s.strip().split('\t', 1)
        return cls.parse_std(std)
        
    @classmethod
    def parse_std(cls, s):
        " Parse back :meth:`RankEntry.format_std`. "
        site, tail = s.strip().split('\t')
        date, rank = tail.split(', ')
        date = datetime.datetime.strptime(date, cls.TS_FORMAT)
        return cls(site=site, date=date, rank=rank)

    @classmethod
    def parse_json(cls, s):
        " Parse back :meth:`RankEntry.format_json`. "
        d = json.loads(s)
        date = datetime.datetime.strptime(d['tstamp'], cls.TS_FORMAT)
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
        date = datetime.datetime.strptime(fname_last, cls.ALEXA_TS_FORMAT)
        with ZipFile(fname) as zf:
            # The archive contains one file named ``top-1m.csv``
            for line in zf.open('top-1m.csv'):
                rank, name = line.decode().strip().split(',', 1)
                yield cls(name, date, int(rank))


def look_up_ranking(site):
    fname = os.path.join(md_cfg.get('location', 'key_files'),
                         '{0}.gz'.format(RankEntry.make_key(site)))
    logger.debug('Looking for {0} in {1}'.format(site, fname))
    result = []
    with vt_comp.GzipFile(fname) as fp:
        for line in fp:
            line = line.decode()
            if md_tools.get_key(line) == site:
                result.append(RankEntry.parse_std(line))
    return result
