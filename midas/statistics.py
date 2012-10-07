# -*- coding: utf-8 -*-
""" Code to find out about common things in both the crunchbase data
and the Top1M data.
"""

import collections

from midas.compat import GzipFile
from midas.compat import urlparse

import crawlcrunch.model.db as ccdb

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
