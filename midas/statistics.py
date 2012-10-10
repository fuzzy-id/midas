# -*- coding: utf-8 -*-
""" Code to find out about common things in both the crunchbase data
and the Top1M data.

What you should do before starting to use this module:

    * generate key files

    * generate a name count

    * fetch all data from crunchbase
"""

import collections
import glob
import math
import operator
import os.path

from sqlalchemy import and_
from sqlalchemy import or_
import crawlcrunch.model.db as ccdb

from midas.compat import GzipFile
from midas.compat import ifilter
from midas.compat import imap
from midas.compat import urlparse
from midas.scripts.alexa_to_key_files import check_and_count_entries

import midas.config as md_cfg

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

def check_sha1_distr_mean_max_min_deviation_variance(root_dir=None):
    if root_dir is None:
        root_dir = md_cfg.get('statistics', 'key_files')
    counter = check_and_count_entries(glob.glob(os.path.join(root_dir, '*')))
    mean = sum(counter.itervalues()) / len(counter) * 1.0
    max_ = max(counter.itervalues())
    min_ = min(counter.itervalues())
    deviation = (sum(math.fabs(x - mean) for x in counter.itervalues())
                 / len(counter))
    variance = deviation**2
    return (mean, max_, min_, deviation, variance)
    

SiteCnt = collections.namedtuple('SiteCount', ['site', 'cnt'])

def get_site_counts(path=None):
    if path is None:
        path = md_cfg.get('statistics', 'site_count')
    with GzipFile(path) as fp:
        for l in fp:
            site, cnt = l.decode().strip().split('\t', 1)
            cnt = int(cnt)
            yield SiteCnt(site, cnt)

def all_sites(path=None):
    return imap(operator.attrgetter('site'), 
                get_site_counts(path=path))

def sites_of_interest(path=None):
    " Iterate all sites not having a path. "
    return ifilter(lambda s: len(s.split('/', 1)) == 1,
                   all_sites(path))

def all_companies():
    " Returns 100355 companies. "
    sess = make_session()
    return sess.query(ccdb.Company).all()

def companies_of_interest():
    """ Returns all companies with a funding round with round_level
    'angel', 'seed' or 'a' since December 2010.
    """
    sess = make_session()
    funding_round_q = sess.query(ccdb.FundingRound).\
        filter(or_(ccdb.FundingRound.funded_year>2010,
                   and_(ccdb.FundingRound.funded_year==2010,
                        ccdb.FundingRound.funded_month==12))).\
        filter(ccdb.FundingRound.round_code.in_(['angel', 'seed', 'a'])).\
        subquery()
    q = sess.query(ccdb.Company).join(funding_round_q,
                                      ccdb.Company.funding_round)
    return q.all()
