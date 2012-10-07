# -*- coding: utf-8 -*-
""" Code to find out about common things in both the crunchbase data
and the Top1M data.
"""

import collections
import glob
import os.path

import crawlcrunch.model.db as ccdb

from midas.compat import GzipFile
from midas.compat import urlparse
from midas.scripts.alexa_to_key_files import check_and_count_entries

import midas.config as md_cfg

def check_sha1_distr_mean_max_min_deviation_variance(root_dir=None):
    if root_dir is None:
        root_dir = md_cfg.get('local_data', 'key_files')
    counter = check_and_count_entries(glob.glob(os.path.join(root_dir, '*'))):
    mean = sum(counter.itervalues()) / len(counter) * 1.0
    max_ = max(counter.itervalues())
    min_ = min(counter.itervalues())
    deviation = (sum(math.fabs(x - mean) for x in counter.itervalues()) 
                 / len(counter))
    variance = deviation ** 2
    return mean, max_, min_, deviation, variance
    

SiteCnt = collections.namedtuple('NameCount', ['site', 'cnt'])

def site_cnt(path):
    with GzipFile(path) as fp:
        for l in fp:
            site, cnt = l.decode().strip().split('\t', 1)
            cnt = int(cnt)
            yield SiteCnt(site, cnt)

def only_hps(sess):
    return set(i[0] for i in sess.query(ccdb.Company)\
                   .filter(ccdb.Company.homepage_url != None)\
                   .filter(ccdb.Company.homepage_url != '').all())

def only_externals(sess):
    return set(i[0] for i in sess.query(ccdb.Company)\
                   .filter(ccdb.Company.external_links != None)\
                   .filter(ccdb.))

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
