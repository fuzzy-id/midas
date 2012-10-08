# -*- coding: utf-8 -*-
""" Code to find out about common things in both the crunchbase data
and the Top1M data.
"""

import collections
import glob
import math
import os.path

import crawlcrunch.model.db as ccdb

from midas.compat import GzipFile
from midas.compat import urlparse
from midas.scripts.alexa_to_key_files import check_and_count_entries

import midas.config as md_cfg

_sess = None

def make_session(db=None):
    global _sess
    if _sess is None:
        if db is None:
            db = md_cfg.get('local_data', 'crunchbase_db')
        engine = ccdb.create_engine(db)
        ccdb.Session.configure(bind=engine)
        _sess = ccdb.Session()
    return _sess

def check_sha1_distr_mean_max_min_deviation_variance(root_dir=None):
    if root_dir is None:
        root_dir = md_cfg.get('local_data', 'key_files')
    counter = check_and_count_entries(glob.glob(os.path.join(root_dir, '*')))
    mean = sum(counter.itervalues()) / len(counter) * 1.0
    max_ = max(counter.itervalues())
    min_ = min(counter.itervalues())
    deviation = (sum(math.fabs(x - mean) for x in counter.itervalues())
                 / len(counter))
    variance = deviation**2
    return (mean, max_, min_, deviation, variance)
    

SiteCnt = collections.namedtuple('NameCount', ['site', 'cnt'])

def site_cnt(path):
    with GzipFile(path) as fp:
        for l in fp:
            site, cnt = l.decode().strip().split('\t', 1)
            cnt = int(cnt)
            yield SiteCnt(site, cnt)

def all_companies():
    " Returns 100355 companies. "
    sess = make_session()
    return sess.query(ccdb.Company).all()

def only_externals(sess):
    return set(i[0] for i in sess.query(ccdb.Company)\
                   .filter(ccdb.Company.external_links != None))

def netloc(url):
    return urlparse(url).netloc

def num_companies(sess):
    return sess.query(ccdb.Company).count()

def common_hp_starts(hps, netloc=False):
    if netloc:
        keyfunc = lambda hp: urlparse(hp).netloc.split('.', 1)[0]
    else:
        keyfunc = lambda hp: hp.split('.', 1)[0]
    return count_keys(hps, keyfunc)
