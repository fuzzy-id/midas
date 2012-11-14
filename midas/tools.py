# -*- coding: utf-8 -*-
""" This module provides common functions which are usually needed in
all other submodules or interactively.
"""

import collections
import datetime
import functools
import itertools
import logging
import operator
import os
import os.path
import subprocess

from vincetools.compat import GzipFile
from vincetools.compat import ifilter
from vincetools.compat import imap
from vincetools.compat import str_type
from vincetools.compat import urlparse
import vincetools.compat as vt_comp

import midas as md
import midas.db as md_db
import midas.config as md_cfg

logger = logging.getLogger(__name__)

def interactive():
    """ Saves us a few lines of typing when using midas
    interactively.
    """
    md_cfg.new_configparser()
    md_cfg.read(os.path.join(os.environ['HOME'], '.midas'))

### Functions that work on MapReduce-style 'key\tvalue' lines ###

def split_key_value(line, sep='\t'):
    return line.strip().split(sep, 1)

def get_key(line, sep='\t'):
    return split_key_value(line, sep)[0]

### Functions that are often needed in interactive use ###

def group_by_key(iterable, keyfunc):
    return imap(operator.itemgetter(1), itertools.groupby(iterable, keyfunc))

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

def count_items(iterable):
    try:
        return len(iterable)
    except TypeError:
        return sum(1 for _ in iterable)

def relation_stats(iterable):
    counter = count_by_key(iterable)
    return (sum(vt_comp.d_itervalues(counter)),
            len(counter), 
            sum(v for v in vt_comp.d_itervalues(counter) if v > 1), 
            sum(1 for v in vt_comp.d_itervalues(counter) if v > 1))

### Functions to query sites and companies ###

def domain(company_or_site):
    """ Return the domain part of an Alexa Top1M site or a
    :class:`crawlcrunch.model.db.Company` instance.
    """
    if isinstance(company_or_site, md_db.Company):
        return urlparse(company_or_site.homepage_url)\
            .netloc.lower()
    elif isinstance(company_or_site, str_type):          # This should be an
        if 'http' in company_or_site:                    # A full URL
            return urlparse(company_or_site).netloc.lower()
        return company_or_site.split('/', 1)[0].lower()  # Alexa Top1M site
    else:
        raise TypeError("cannot extract domain part: {0}".format(
                type(company_or_site)))

def iter_all_companies():
    " Returns 100355 companies. "
    sess = md_db.db_session()
    return sess.query(md_db.Company).all()

def iter_interesting_companies():
    """ Returns all companies having a funding round with
    `round_level` ``angel``, ``seed`` or ``a`` since December 2010.
    """
    q = md_db.q_c_w_hp_url()
    q = q.join(md_db.q_fr_of_interest().subquery())
    return q.all()

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

def make_number_of_funding_rounds_plot(interactive=True):
    fr_dates = [ datetime.date(fr.funded_year, fr.funded_month, fr.funded_day)
                 for fr in md_db.q_fr_of_interest().all() ]
    cnt = count_by_key(fr_dates)
    xs = sorted(vt_comp.d_iterkeys(cnt))
    ys = [ cnt[x] for x in xs ]
    if not 'DISPLAY' in os.environ:
        import matplotlib
        try:
            matplotlib.use('Agg')
        except UserWarning:
            pass
    import matplotlib.pyplot as plt
    fig = plt.figure()

    ax = fig.add_subplot(111)
    ax.plot(xs, ys)
    fig.autofmt_xdate()
    plt.grid(True)
    plt.ylabel('Raised Fundings with Code A, Angel or Seed')
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
    xs = sorted(cnt_pessimistic.keys())
    ys_pessimistic = [ cnt_pessimistic[x] for x in xs ]
    xs_pessimistic = [ x.days for x in xs ]
    xs = sorted(cnt_optimistic.keys())
    ys_optimistic = [ cnt_optimistic[x] for x in xs ]
    xs_optimistic = [ x.days for x in xs ]
    if not 'DISPLAY' in os.environ:
        import matplotlib
        try:
            matplotlib.use('Agg')
        except UserWarning:
            pass
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(xs_pessimistic, ys_pessimistic, 'r.', 
            label='w/o Gaps until Fund Raise')
    ax.plot(xs_optimistic, ys_optimistic, 'b.',
            label='First Occurence until Fund Raise')
    plt.grid(True)
    plt.xlabel('Number of Days')
    plt.ylabel('Occurences')
    if interactive:
        plt.show()
    else:
        img = os.path.join(md_cfg.get('location', 'home'),
                           'occurences_per_timedelta.png')
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

def make_filter_by_date(start, end):
    def date_filter(funding_round, entries):
        funding_date = datetime.datetime(funding_round.funded_year,
                                         funding_round.funded_month,
                                         funding_round.funded_day)
        for entry in entries:
            if ((funding_date - start) 
                <= entry.date 
                <= (funding_date - end)):
                yield entry
    return date_filter

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
