# -*- coding: utf-8 -*-
""" Code to find out about common things in both the crunchbase data
and the Top1M data.
"""

import crawlcrunch.model.db as ccdb

def hps(sess):
    return [ i[0] for i in sess.query(ccdb.Company.homepage_url)\
                 .filter(ccdb.Company.homepage_url != None)\
                 .filter(ccdb.Company.homepage_url != '').all() ]

def netloc(url):
    return urlparse(url).netloc

def num_companies(sess):
    return sess.query(ccdb.Company).count()

def common_starts(iterable):
    counter = collections.defaultdict(int)
    for item in iterable:
        start = item.split('.', 1)[0]
        counter[start] += 1
    return counter
