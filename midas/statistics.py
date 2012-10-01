# -*- coding: utf-8 -*-
""" Code to find out about common things in both the crunchbase data
and the Top1M data.
"""

import collections

import crawlcrunch.model.db as ccdb

def hps(sess):
    return [ i[0] for i in sess.query(ccdb.Company.homepage_url)\
                 .filter(ccdb.Company.homepage_url != None)\
                 .filter(ccdb.Company.homepage_url != '').all() ]

def netloc(url):
    return urlparse(url).netloc

def num_companies(sess):
    return sess.query(ccdb.Company).count()

def count_keys(iterable, keyfunc):
    counter = collections.defaultdict(int)
    for item in iterable:
        counter[keyfunc(item)] += 1
    return counter

def collect_by_key(iterable, keyfunc):
    collected = collection.defaultdict(list)
    for item in iterable:
        collected[keyfunc(item)].append(item)
    return collected

def common_hp_starts(hps, netloc=False):
    if netloc:
        keyfunc = lambda hp: netloc(hp).split('.', 1)[0]
    else:
        keyfunc = lambda hp: hp.split('.', 1)[0]
    return count_keys(hps, keyfunc)
