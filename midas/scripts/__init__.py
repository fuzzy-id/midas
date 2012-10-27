# -*- coding: utf-8 -*-
""" This module provides classes to easily create scripts which can be
used from the command-line.
"""

import argparse
import logging
import os.path
import sys

import midas.config as md_cfg

logger = logging.getLogger(__name__)


class MDCommand(object):
    """ Initializes the :class:`MDCommand` instance by passing `argv`
    to :meth:`parser` and configuring :mod:`logging`. If `argv` is
    ``None`` :obj:`sys.argv` is passed to the parser.

    Subclass this to write an easy to use command line interface to
    your function. But, make sure to call this class's
    :meth:`__init__` method when over-writing it.
    """

    POS_ARG = None

    def __init__(self, argv=None):
        if argv is None:  # pragma: no cover
            argv = sys.argv
        self.args = self.parser.parse_args(argv[1:])

        md_cfg.read(os.path.expanduser(self.args.cfg))

        self.args.verbosity.append(
            logging.getLevelName(md_cfg.get('handler_console', 'level')))
        md_cfg.set('handler_console', 'level', 
                   logging.getLevelName(sum(self.args.verbosity)))
        md_cfg.configure_logging()
    
    @classmethod
    def cmd(cls, argv=None):
        """ Initiates the class and calls its :meth:`run`
        method. Returns whatever :meth:`run` returns, except for
        :obj:`None` which is interpreted as `0` (integer zero).
        """
        obj = cls(argv)
        ret_val = obj.run()
        # `None` means everything's fine
        return 0 if ret_val is None else ret_val

    def run(self):  # pragma: no cover
        """ Overwrite this method with the code you want your command
        to execute. Return an integer unequal `0` if you want to
        signal that something went wrong.
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
