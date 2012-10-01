# -*- coding: utf-8 -*-
""" Common functions that are needed in most other submodules.
"""

import argparse
import datetime
import hashlib
import logging
import os.path
import sys

from midas.compat import ZipFile

SAMPLE_CONFIG = """
[DEFAULTS]
user_name = thbach
hadoop_home = hdfs://localhost:9000/user/%(user_name)s
local_home = /home/$(user_name)s

[job]
mappers = 16
reducers = 28

[alexa]
top1m_files = %(hadoop_home)s/alexa-files#alexa-files
crunchbase_db = sqlite:////$(local_home)s/ba_data/crunchbase_db.sql
cut_hash_key = 3

[hadoop]
home = %(local_home)s/opt/hadoop-1.0.3
exec = %(home)s/bin/hadoop
streaming = %(home)/contrib/streaming/hadoop-streaming-1.0.3.jar

[loggers]
keys = root

[handlers]
keys = stderr

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = stderr

[handler_stderr]
class = StreamHandler
args = (sys.stderr, )
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s %(message)s
"""

#: How much letters of the hash key should be used to pre-sort the
#: entries. The larger this number the more and smaller files
#: will be produced. The default value is `2` which gives us `16 * 16 =
#: 256` files.
CUT_HASH_KEY = 3

class MDCommand(object):
    """ Subclass this to write an easy to use command line interface to
    your function.
    """

    def __init__(self, argv):
        self.args = self.parser.parse_args(argv[1:])
        self.args.verbosity = sum(self.args.verbosity)
        logging.basicConfig(level=self.args.verbosity, stream=sys.stderr)

    @classmethod
    def cmd(cls, argv=sys.argv):
        obj = cls(argv)
        return obj.run()

    def run(self):
        """ Overwrite this method with the code you want your command
        to execute. Return 0 on success, otherwise an other integer.
        """
        raise NotImplementedError()

    @property
    def parser(self):
        """ Returns a :class:`argparse.ArgumentParser` object having
        `--verbose`, `--quiet` flags and reads from `stdin`.
        """
        if not hasattr(self, '_parser'):
            parser = argparse.ArgumentParser(description=self.__doc__)
            parser.add_argument('-v', '--verbose', dest='verbosity',
                                action='append_const', const=-10,
                                help='be more verbose, can be given once',
                                default=[logging.getLevelName('INFO')])
            parser.add_argument('-q', '--quiet', dest='verbosity',
                                action='append_const', const=10,
                                help='be quieter, can be given up to three times')
            parser.add_argument('stream', nargs='*', metavar='FILE', default=sys.stdin,
                                help='the files to read')
            self._parser = parser
            self.add_argument()
        return self._parser

    def add_argument(self):
        """ Overwrite this function to add further arguments to
        :attr:`self.parser`.
        """
        pass

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
        return 'RankEntry({e.name}, {e.tstamp}, {e.rank})'.format(e=self)

    def __eq__(self, other):
        return (self.name == other.name
                and self.date == other.date
                and self.rank == other.rank)

    def __lt__(self, other):
        if self.name < other.name:
            return True
        elif self.name > other.name:
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
        " `'name[TAB]tstamp,[SPACE]rank'`. "
        return '{e.name}\t{e.tstamp}, {e.rank}'.format(e=self)

    @property
    def tstamp(self):
        " Return the `date` formated as defined in :attr:`TS_FORMAT`. "
        return self.date.strftime(self.TS_FORMAT)

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
            self._key = self.make_key(self.name)
        return self._key

    @classmethod
    def make_key(cls, s):
        sha1 = hashlib.sha1(s.encode()).hexdigest()
        return sha1[:CUT_HASH_KEY]
        

    @classmethod
    def parse_key(cls, s):
        key, std = s.strip().split('\t', 1)
        return cls.parse_std(std)
        
    @classmethod
    def parse_std(cls, s):
        name, tail = s.strip().split('\t')
        date, rank = tail.split(', ')
        date = datetime.datetime.strptime(date, cls.TS_FORMAT)
        return cls(name=name, date=date, rank=rank)

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
