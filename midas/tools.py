# -*- coding: utf-8 -*-
""" This module provides common functions which are usually needed in
all other submodules or interactively.
"""

import collections
import datetime
import functools
import itertools
import operator
import os
import os.path
import subprocess

from midas.compat import GzipFile
from midas.compat import ifilter
from midas.compat import imap
from midas.compat import urlparse
import midas.compat as vt_comp

import midas as md


### Functions that work on MapReduce-style 'key\tvalue' lines ###

def split_key_value(line, sep='\t'):
    return line.strip().split(sep, 1)

def get_key(line, sep='\t'):
    return split_key_value(line, sep)[0]

### Functions that are often needed in interactive use ###

def count_by_key(iterable, keyfunc=lambda o: o):
    counter = collections.defaultdict(int)
    for item in iterable:
        counter[keyfunc(item)] += 1
    return counter

def collect_by_key(iterable, keyfunc):
    collected = collections.defaultdict(list)
    for item in iterable:
        collected[keyfunc(item)].append(item)
    return collected

def relation_stats(iterable):
    counter = count_by_key(iterable)
    return (sum(vt_comp.d_itervalues(counter)),
            len(counter), 
            sum(v for v in vt_comp.d_itervalues(counter) if v > 1), 
            sum(1 for v in vt_comp.d_itervalues(counter) if v > 1))

### Functions to query sites and companies ###

SiteCount = collections.namedtuple('SiteCount', ['site', 'count'])

def iter_site_counts(path=None):
    " Iterate over a site-count file. "
    if path is None:
        path = md_cfg.get('location', 'site_count')
    with GzipFile(path) as fp:
        for l in fp:
            site, cnt = split_key_value(l.decode())
            yield SiteCount(site, int(cnt))

def iter_all_sites(path=None):
    " Iterate over all sites found in a site-count file. "
    return imap(operator.attrgetter('site'), 
                iter_site_counts(path=path))

def iter_interesting_sites(path=None):
    """ Iterate over all sites found in a site-count file. Sites that
    have a path are filtered out.
    """
    return ifilter(lambda s: len(s.split('/', 1)) == 1,
                   iter_all_sites(path))

def make_p_empty_attr(attr_name):
    def p_empty_attr(o):
        attr = getattr(o, attr_name)
        return attr is None or attr == ''
    return p_empty_attr

### Useful miscelanious stuff ###

def make_number_of_funding_rounds_plot(
    companies, plot_name='./funding_rounds_per_date.png'
    ):
    fr_dates = [ datetime.date(fr.funded_year, fr.funded_month, fr.funded_day)
                 for fr in md_db.q_fr_of_interest().all() ]
    cnt = count_by_key(fr_dates)
    xs = sorted(vt_comp.d_iterkeys(cnt))
    ys = [ cnt[x] for x in xs ]
    if not 'DISPLAY' in os.environ:
        import matplotlib
        try:
            matplotlib.use('Agg')
        except UserWarning:  # pragma: no cover
            pass
    import matplotlib.pyplot as plt
    fig = plt.figure()

    ax = fig.add_subplot(111)
    ax.plot(xs, ys)
    fig.autofmt_xdate()
    plt.grid(True)
    plt.ylabel('Funding Rounds with Code A, Angel or Seed')
    plt.title('Number of Funding Rounds per Date')
    if interactive:
        plt.show()
    else:
        img = os.path.join(md_cfg.get('location', 'home'),
                           'funding_rounds_per_date.png')
        plt.savefig(img, bbox_inches=0)
        plt.close()

def make_ts_length_plot(interactive=True):
    ts_d = dict(
        (site, list(sub_iter))
        for site, sub_iter in itertools.groupby(iter_associated_time_series(),
                                                operator.attrgetter('site'))
        )
    funds_site_date_iter = ( (fr.company.site.site, 
                              datetime.datetime(fr.funded_year,
                                                fr.funded_month,
                                                fr.funded_day))
                             for fr in md_db.q_fr_of_interest().all()
                             if fr.company.site is not None )
    data = ( list(filter(lambda e: e.date <= date, ts_d[site]))
             for site, date in funds_site_date_iter 
             if site in ts_d )
    data_n_empty = [ sorted(e.date for e in l)
                     for l in data if len(l) > 0 ]
    dates = all_dates()
    iter_pessimistic = ( list(iter_ts_until_gap(l, dates))
                         for l in data_n_empty )
    cnt_pessimistic = count_by_key(iter_pessimistic, lambda l: l[0] - l[-1])
    cnt_optimistic = count_by_key(data_n_empty, lambda l: l[-1] - l[0])
    ys_pessimistic = [ 
        cnt_pessimistic.get(datetime.timedelta(x), 0)
        for x in range(min(vt_comp.d_iterkeys(cnt_pessimistic)).days,
                       max(vt_comp.d_iterkeys(cnt_pessimistic)).days) 
        ]
    ys_optimistic = [ 
        cnt_optimistic.get(datetime.timedelta(x), 0)
        for x in range(min(vt_comp.d_iterkeys(cnt_optimistic)).days,
                       max(vt_comp.d_iterkeys(cnt_optimistic)).days) 
        ]
    if not 'DISPLAY' in os.environ:
        import matplotlib
        try:
            matplotlib.use('Agg')
        except UserWarning:  # pragma: no cover
            pass
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(ys_pessimistic, label='First Gap to Fund Raise',
            cumulative=True, histtype='step', 
            bins=len(ys_pessimistic)/15)
    ax.hist(ys_optimistic, label='First Occurence to Fund Raise',
            cumulative=True, histtype='step',
            bins=len(ys_optimistic)/15)
    plt.grid(True)
    plt.xlabel('Available Days')
    plt.ylabel('Count')
    if interactive:
        plt.show()
    else:
        img = os.path.join(md_cfg.get('location', 'home'),
                           'hist_count_available_days.png')
        plt.savefig(img, bbox_inches=0)
        plt.close()

def iter_associated_time_series():
    sites = set(md_db.iter_sites_in_associations())
    sites_f = md_cfg.get('location', 'sites')
    with vt_comp.GzipFile(sites_f) as fp:
        for line in fp:
            site, tstamp, rank = line.decode().strip().split('\t')
            if site in sites:
                date = md.parse_tstamp(tstamp)
                yield md.RankEntry(site, date, int(rank))

def all_dates():
    return sorted( md.parse_tstamp(d.split('_')[-1].split('.')[0])
                   for d in os.listdir('/data0/alexa_files/') )

def takewhile_common(list1, list2):
    for a, b in zip(list1, list2):
        if a != b:
            break
        yield a

def iter_ts_until_gap(ts, all_dates):
    first_common = all_dates.index(ts[-1])
    return takewhile_common(ts[::-1], all_dates[first_common::-1])
