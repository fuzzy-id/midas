# -*- coding: utf-8 -*-
""" This module provides classes to easily create scripts which can be
used from the command-line.
"""

from __future__ import print_function

import argparse
import os.path
import sys


class CheckDirectoryAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            parser.error("the directory '{0}' does not exist".format(
                    values))
        setattr(namespace, self.dest, values)


class MDCommand(object):
    """ Initializes the :class:`MDCommand` instance by passing `argv`
    to :meth:`parser` and configuring :mod:`logging`. If `argv` is
    ``None`` :obj:`sys.argv` is passed to the parser.

    Subclass this to write an easy to use command line interface to
    your function. But, make sure to call this class's
    :meth:`__init__` method when over-writing it.
    """

    _out = sys.stdout

    def __init__(self, argv=None):
        if argv is None:  # pragma: no cover
            argv = sys.argv
        self.args = self.parser.parse_args(argv[1:])
    
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
            parser.add_argument('-q', '--quiet', action='store_true',
                                help='Suppress status messages')
            self._parser = parser
            self.add_argument()
        return self._parser

    def add_argument(self):  # pragma: no cover
        """ Overwrite this function to add further arguments to
        :attr:`self.parser`. This function is called before the actual
        arguments are passed in :meth:`__init__`.
        """
        pass

    def out(self, msg):
        if not self.args.quiet:
            print(msg, file=self._out)
