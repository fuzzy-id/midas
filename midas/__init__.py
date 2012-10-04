# -*- coding: utf-8 -*-
""" Common functions that are needed in most other submodules.
"""

import argparse
import datetime
import hashlib
import logging.config
import os
import os.path
import sys

from midas.compat import ConfigParser
from midas.compat import StringIO
from midas.compat import ZipFile


DEFAULT_CONFIG = """
[DEFAULTS]
user_name = {env[USER]}
hdfs_home = hdfs://localhost:9000/user/%(user_name)s
local_home = {env[HOME]}

[job]
mapper = /path/to/mapper
num_mappers = 16
reducer = /path/to/reducer
num_reducers = 28
input = None
output = None
compress_output = true

[alexa]
top1m_files = %(hdfs_home)s/alexa-files#alexa-files
crunchbase_db = sqlite:////$(local_home)s/ba_data/crunchbase_db.sql
key_length = 3

[hadoop]
home = %(local_home)s/opt/hadoop-1.0.3
exec = %(home)s/bin/hadoop
streaming = %(home)s/contrib/streaming/hadoop-streaming-1.0.3.jar

[loggers]
keys = root

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = DEBUG
handlers = console

[handler_console]
class = StreamHandler
args = (sys.stderr, )
level = INFO
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s %(message)s
""".format(env=os.environ)

#: How much letters of the hash key should be used to pre-sort the
#: entries. The larger this number the more and smaller files
#: will be produced. The default value is `2` which gives us `16 * 16 =
#: 256` files.
CUT_HASH_KEY = 3

class MDCommand(object):
    """ Initializes the :class:`MDCommand` instance by passing `argv`
    (usually :obj:`sys.argv`) to :meth:`parser` and configuring the
    :mod:`logging`.

    Subclass this to write an easy to use command line interface to
    your function. But, make sure to call this class's
    :meth:`__init__` method when over-writing it.
    """

    POS_ARG = None

    def __init__(self, argv):
        self.args = self.parser.parse_args(argv[1:])
        self._configure_logging()
    
    def _configure_logging(self):
        console_severity = self.config.get('handler_console', 'level')
        level_as_int = logging.getLevelName(console_severity)
        new_level = level_as_int + sum(self.args.verbosity)
        self.config.set('handler_console', 'level', 
                        logging.getLevelName(new_level))
        buf = StringIO()
        self.config.write(buf)
        buf.seek(0)
        logging.config.fileConfig(buf)

    @classmethod
    def cmd(cls, argv=sys.argv):
        """ Initiates the class and calls its :meth:`run`
        method. Returns whatever :meth:`run` returns, except for
        :obj:`None` which is interpreted as `0` (integer zero).
        """
        obj = cls(argv)
        ret_val = obj.run()
        # `None` means everything's fine
        return 0 if ret_val is None else ret_val

    def run(self):
        """ Overwrite this method with the code you want your command
        to execute. Return an integer unequal `0` if you want to
        signal that something went wrong.
        """
        raise NotImplementedError()

    @property
    def config(self):
        """ Returns a :class:`midas.compat.ConfigParser` object having
        parsed :const:`DEFAULT_CONFIG` first and the configuration
        file as given to :meth:`parser` second.
        """
        if not hasattr(self, '_config'):
            cp = ConfigParser()
            cp.read_string(DEFAULT_CONFIG)
            cp.read(os.path.expanduser(self.args.cfg))
            self._config = cp
        return self._config

    @property
    def parser(self):
        """ Returns a :class:`argparse.ArgumentParser` object having
        `--verbose`, `--quiet` flags and reads from `stdin`.
        """
        if not hasattr(self, '_parser'):
            parser = argparse.ArgumentParser(description=self.__doc__)
            parser.add_argument('-v', '--verbose', dest='verbosity',
                                action='append_const', const=-10,
                                help='decrease the severity of the console handler',
                                default=[0])
            parser.add_argument('-q', '--quiet', dest='verbosity',
                                action='append_const', const=10,
                                help='increase the severity of the console handler')
            parser.add_argument('-c', '--cfg', default='~/.midas',
                                help=' '.join(('the midas configuration file,',
                                               'default is "~/.midas"')))
            if self.POS_ARG:
                parser.add_argument(**self.POS_ARG)
            self._parser = parser
            self.add_argument()
        return self._parser

    def add_argument(self):
        """ Overwrite this function to add further arguments to
        :attr:`self.parser`. This function is called before the actual
        arguments are passed in :meth:`__init__`.
        """
        pass

class MDJob(MDCommand):
    " Provides :class:`MDCommand` with a positional argument. "
    
    POS_ARG = {'dest': 'stream', 
               'nargs': '*',
               'metavar': 'RECORD', 
               'default': sys.stdin, 
               'help': 'the records to read'}


class RankEntry(object):
    """ Returns an entry of a ranking for `name`.

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
