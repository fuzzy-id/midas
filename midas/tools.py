# -*- coding: utf-8 -*-

import collections
import functools
import itertools
import logging
import operator
import subprocess

from vincetools.compat import ifilter
from vincetools.compat import imap
from vincetools.compat import urlparse

logger = logging.getLogger(__name__)

def domain(company_or_site):
    """ Return the domain part of an Alexa Top1M site or a
    :class:`crawlcrunch.model.db.Company` instance.
    """
    if isinstance(obj, ccdb.Company):
        return urlparse(company_or_site.homepage_url).netloc.lower()
    elif isinstance(obj, str):  # This should be an Alexa Top1M site
        return company_or_site.split('/', 1)[0].lower()
    else:
        raise TypeError("cannot extract domain part: '{0}'".format(type(company_or_site)))

def lookup_ranking(site, key_dir):
    key = RankEntry.make_key(site)
    fname = os.path.join(key_dir, '{0}.gz'.format(key))
    entries = []
    with GzipFile(fname) as fp:
        pred = lambda l: RankEntry.parse_std(l.decode()).site != site
        for line in itertools.dropwhile(pred, fp):
            entry = RankEntry.parse_std(line.decode())
            if entry.site == site:
                yield entry
            else:
                break

def group_by_key(iterable, sep='\t'):
    keyfunc = functools.partial(key, sep=sep)
    return imap(operator.itemgetter(1), itertools.groupby(iterable, keyfunc))

def count_items(iterable):
    try:
        return len(iterable)
    except TypeError:
        return sum(1 for _ in iterable)

def count_by_key(iterable, keyfunc):
    counter = collections.defaultdict(int)
    for item in iterable:
        counter[keyfunc(item)] += 1
    return counter

def collect_by_key(iterable, keyfunc):
    collected = collection.defaultdict(list)
    for item in iterable:
        collected[keyfunc(item)].append(item)
    return collected

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
