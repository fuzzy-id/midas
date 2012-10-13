# -*- coding: utf-8 -*-
""" This module provides common functions which are usually needed in
all other submodules or interactively.
"""

import collections
import functools
import itertools
import logging
import operator
import subprocess

from vincetools.compat import ifilter
from vincetools.compat import imap
from vincetools.compat import urlparse

from crawlcrunch.model.db import Company
from crawlcrunch.model.db import FundingRound

logger = logging.getLogger(__name__)

def domain(company_or_site):
    """ Return the domain part of an Alexa Top1M site or a
    :class:`crawlcrunch.model.db.Company` instance.
    """
    if isinstance(obj, Company):
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

def iter_interesting_companies():
    """ Returns all companies having a funding round with round_level
    'angel', 'seed' or 'a' since December 2010.
    """
    sess = md_tools.make_session()
    funding_round_subq = sess.query(ccdb.FundingRound).\
        filter(ccdb.FundingRound.round_code.in_(['angel', 'seed', 'a'])).\
        filter(or_(ccdb.FundingRound.funded_year>2010,
                   and_(ccdb.FundingRound.funded_year==2010,
                        ccdb.FundingRound.funded_month==12))).subquery()
    q = sess.query(ccdb.Company).join(funding_round_subq,
                                      ccdb.Company.funding_round)
    return q.all()

_sess = None

def make_session(db=None):
    global _sess
    if _sess is None:
        if db is None:
            db = md_cfg.get('statistics', 'crunchbase_db')
        engine = ccdb.create_engine(db)
        ccdb.Session.configure(bind=engine)
        _sess = ccdb.Session()
    return _sess

SiteCount = collections.namedtuple('SiteCount', ['site', 'cnt'])

def iter_site_counts(path=None):
    if path is None:
        path = md_cfg.get('statistics', 'site_count')
    with GzipFile(path) as fp:
        for l in fp:
            site, cnt = l.decode().strip().split('\t', 1)
            cnt = int(cnt)
            yield SiteCount(site, cnt)

def iter_all_sites(path=None):
    return imap(operator.attrgetter('site'), 
                get_site_counts(path=path))

def sites_of_interest(path=None):
    " Iterate all sites not having a path. "
    return ifilter(lambda s: len(s.split('/', 1)) == 1,
                   all_sites(path))

def iter_all_companies():
    " Returns 100355 companies. "
    sess = make_session()
    return sess.query(ccdb.Company).all()

