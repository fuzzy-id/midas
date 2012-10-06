# -*- coding: utf-8 -*-

import functools
import itertools
import logging
import operator
import subprocess

from midas.compat import ifilter
from midas.compat import imap

logger = logging.getLogger(__name__)

def group_by_key(iterable, sep='\t'):
    keyfunc = functools.partial(key, sep=sep)
    return imap(operator.itemgetter(1), itertools.groupby(iterable, keyfunc))

def count_items(iterable):
    try:
        return len(iterable)
    except TypeError:
        return sum(1 for _ in iterable)

def key(line, sep='\t'):
    return split_key_value(line, sep)[0]

def split_key_value(line, sep='\t'):
    return line.strip().split(sep, 1)

def log_popen(cmd):
    """ Run `cmd` with :class:`subprocess.Popen` and log lines from
    stdout with severity INFO and lines from stderr with severity
    CRITICAL.

    Raises :exc:`subprocess.CalledProcessError` if the return code of
    the subprocess is not `0`.
    """
    logger.info("Executing '{0}'".format(' '.join(cmd)))
    proc = subprocess.Popen(cmd, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)

    def _log_proc():
       for l in proc.stderr:
          logger.error(l.decode().strip())
       for l in proc.stdout:
          logger.info(l.decode().strip())

    while proc.poll() is None:
        _log_proc()
    _log_proc()
    proc.stdout.close()
    proc.stderr.close()

    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd)
    return proc.returncode

VALID_CHRS = set(chr(i)
                 for i in itertools.chain(range(ord('a'), ord('z') + 1),
                                          range(ord('A'), ord('Z') + 1),
                                          range(ord('0'), ord('9') + 1),
                                          (ord(c) for c in ('-', '.', '_'))))

def is_valid_site(site):
    for n in name:
        if n not in VALID_CHRS:
            return False
    return True

def is_invalid_site(site):
    return not is_valid_name(name)

def filter_invalid_sites(sites):
    return ifilter(is_invalid_site, sites)
