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
from crawlcrunch.model.db import Session
from crawlcrunch.model.db import create_engine

from sqlalchemy import and_
from sqlalchemy import or_

import midas.config as md_cfg

logger = logging.getLogger(__name__)

### Functions that work on MapReduce-style 'key\tvalue' lines ###

def split_key_value(line, sep='\t'):
    return line.strip().split(sep, 1)

def get_key(line, sep='\t'):
    return split_key_value(line, sep)[0]

### Functions that are often needed in interactive use ###

def group_by_key(iterable, keyfunc):
    return imap(operator.itemgetter(1), itertools.groupby(iterable, keyfunc))

def count_by_key(iterable, keyfunc):
    counter = collections.defaultdict(int)
    for item in iterable:
        counter[keyfunc(item)] += 1
    return counter

def collect_by_key(iterable, keyfunc):
    collected = collections.defaultdict(list)
    for item in iterable:
        collected[keyfunc(item)].append(item)
    return collected

def count_items(iterable):
    try:
        return len(iterable)
    except TypeError:
        return sum(1 for _ in iterable)

### Functions to query sites and companies ###

def domain(company_or_site):
    """ Return the domain part of an Alexa Top1M site or a
    :class:`crawlcrunch.model.db.Company` instance.
    """
    if isinstance(company_or_site, Company):
        return urlparse(company_or_site.homepage_url)\
            .netloc.lower()
    elif isinstance(company_or_site, str):               # This should be an
        return company_or_site.split('/', 1)[0].lower()  # Alexa Top1M site
    else:
        raise TypeError(format("cannot extract domain part: '{0}'",
                               type(company_or_site)))

_session = None

def db_session(db=None):
    """ Create a session for the CrunchBase database and return
    it. Subsequent calls will return the same session.
    """
    global _session
    if _session is None:
        if db is None:
            db = md_cfg.get('location', 'crunchbase_db')
        engine = create_engine(db)
        Session.configure(bind=engine)
        _session = Session()
    return _session

def iter_all_companies():
    " Returns 100355 companies. "
    sess = db_session()
    return sess.query(Company).all()

def iter_interesting_companies():
    """ Returns all companies having a funding round with round_level
    'angel', 'seed' or 'a' since December 2010.
    """
    sess = db_session()
    funding_round_subq = sess.query(FundingRound)\
        .filter(FundingRound.round_code.in_(['angel', 'seed', 'a']))\
        .filter(or_(FundingRound.funded_year>2010,
                   and_(FundingRound.funded_year==2010,
                        FundingRound.funded_month==12))).subquery()
    q = sess.query(Company)\
        .filter(Company.homepage_url != None)\
        .filter(Company.homepage_url != '')\
        .join(funding_round_subq, Company.funding_rounds)
    return q.all()

SiteCount = collections.namedtuple('SiteCount', ['site', 'cnt'])

def iter_site_counts(path=None):
    " Iterate over a site-count file. "
    if path is None:
        path = md_cfg.get('location', 'site_count')
    with GzipFile(path) as fp:
        for l in fp:
            site, cnt = split_key_value(l.decode())
            cnt = int(cnt)
            yield SiteCount(site, cnt)

def iter_all_sites(path=None):
    " Iterate over all sites found in a site-count file. "
    return imap(operator.attrgetter('site'), 
                iter_site_counts(path=path))

def iter_interesting_sites(path=None):
    """ Iterate over all sites found in a site-count file. Sites that
    have a path are filtered out.
    """
    return ifilter(lambda s: len(s.split('/', 1)) == 1,
                   all_sites(path))

### Useful miscelanious stuff ###

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
