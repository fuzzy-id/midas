# -*- coding: utf-8 -*-

import collections
import datetime
import string

import matplotlib.dates
import matplotlib.pyplot as plt
import numpy
import operator
import pandas

from midas.compat import imap
from midas.compat import str_type
from midas.see5 import calculate_recall_precision
from midas.see5 import calculate_tpr
from midas.see5 import calculate_fpr
from midas.tools import iter_files_content
from midas.pig_schema import FLATTENED_PARSER
from midas.pig_schema import SITES_W_COMPANY_PARSER


def iter_sites_w_company(directory_or_file):
    contents = iter_files_content(directory_or_file)
    for swc in imap(SITES_W_COMPANY_PARSER, contents):
        ranks = map(operator.attrgetter('rank'), swc.ranking)
        index = pandas.DatetimeIndex(map(operator.attrgetter('tstamp'),
                                       swc.ranking))
        ts = pandas.Series(ranks, index=index)
        tstamp = pandas.Timestamp(swc.tstamp)
        yield (swc.site, ts, swc.company, swc.code, tstamp)


##################################
## Funding Rounds per date Plot ##
##################################

def make_fr_per_date_plot(companies, plot_file=None):
    contents = iter_files_content(companies)
    d = collections.defaultdict(list)
    min_date = datetime.date(2011, 3, 1)
    months = set()
    for c in imap(FLATTENED_PARSER, contents):
        if c.tstamp >= min_date:
            d[c.code].append(matplotlib.dates.date2num(c.tstamp))
            months.add(datetime.date(c.tstamp.year, c.tstamp.month, 1))
    
    months = sorted(months)

    right_border = months[-1] + datetime.timedelta(31)
    right_border = datetime.date(right_border.year, right_border.month, 1)
    months.append(right_border)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(d.values(), label=map(str.title, d.keys()),
            bins=matplotlib.dates.date2num(months))
    ax.set_xlim(matplotlib.dates.date2num(months[0]),
                matplotlib.dates.date2num(months[-1]))
    ax.legend()
    ax.xaxis.set_major_locator(
        matplotlib.dates.MonthLocator(bymonthday=15, interval=2)
        )
    ax.xaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(
            lambda d, _: matplotlib.dates.num2date(d).strftime('%B %Y')
            )
        )
    fig.autofmt_xdate()
    ax.set_ylabel('Number of Funding Rounds')
    ax.grid(True, axis='y')
    if plot_file:
        plt.savefig(plot_file)
    return fig

#########################################
## Available Days Before Funding Round ##
#########################################

def get_available_days_before_fr(ts, fr):
    site, date, code = fr
    date = pandas.Timestamp(date)
    ts_site = ts[site].dropna()
    return code, (ts_site.index[0] - date).days

def make_available_days_before_funding_rounds_plot(sites_w_company,
                                                   plot_file=None):
    collected = collections.defaultdict(list)
    for site, ts, company, code, tstamp in sites_w_company:
        ts = ts.dropna()
        available_days = (ts.index[0] - tstamp).days
        if available_days > 365:
            available_days = 400
        elif available_days < 0:
            available_days = -40
        collected[code].append(available_days)
    fig = plt.figure()
    ax = fig.add_subplot('111')
    res = ax.hist(collected.values(), 
                  bins=10, 
                  histtype='bar', 
                  label=map(string.capitalize, collected.keys()),
                  log=True)
    ax.legend(loc='best')
    ax.set_ylabel('Number of Funding Rounds')
    ax.set_xlabel('Number of Days')
    ax.grid(which='both')
    if plot_file:
        plt.savefig(plot_file)
    return fig

#########################################
## Median of Rank before Funding Round ##
#########################################

def median_rank_of_ts_in_period(ts, start_date, offset):
    period = ts[start_date:(start_date + offset)].dropna()
    return period.median()

def make_rank_before_funding_plot(sites_w_company, 
                                  plot_file=None):
    start = pandas.DateOffset(days=125)
    offset = pandas.DateOffset(days=10)
    collected = collections.defaultdict(list)
    for site, ts, company, code, tstamp in sites_w_company:
        median = median_rank_of_ts_in_period(ts, tstamp - start, offset)
        collected[code].append(median)
    fig = plt.figure()
    ax = fig.add_subplot('111')
    res = ax.hist(collected.values(),
                  label=map(string.capitalize, collected.keys()))
    ax.legend(loc='best')
    ax.grid(True)
    ax.set_xlabel('Rank')
    ax.set_ylabel('Number of Funding Rounds')
    if plot_file:
        plt.savefig(plot_file)
    return fig

def calculate_and_make_rank_before_funding_plot(ts, frs, start_d, end_d, keys=('seed', 'angel', 'a'), **kwargs):
    if 0 < start_d < end_d:
        first = start_d
        snd = '{} days after'.format(end_d)
    elif start_d < end_d < 0:
        first = start_d * -1
        snd = '{} days before'.format(end_d * -1)
    elif start_d < 0 < end_d:
        first = '{} days before'.format(start_d * -1)
        snd = '{} days after'.format(end_d)
    elif 0 == start_d < end_d:
        first = 'Fund Raise'
        snd = '{} days after'.format(end_d)
    elif start_d < end_d == 0:
        first = '{} days before'.format(start_d * -1)
        snd = ''
    else:
        raise ValueError('start_d must be smaller then end_d')

    title = 'Median of Rank from {} to {} Fund Raise'.format(first, snd)    
            
    data = median_rank_before_funding(ts, frs, start_d, end_d)
    return make_rank_before_funding_plot(data, title, keys, **kwargs)

###########################
## Recall Precision Plot ##
###########################

def make_recall_precision_plot(results):
    """
    ``results`` should be the result of `midas.see5.main`
    """
    fig = plt.figure()
    ax = fig.add_subplot('111')
    ax.set_ylabel('Precision')
    ax.set_xlabel('Recall')
    for args, per_cost_result in results.items():
        xs = []
        ys = []
        for x, y in map(calculate_recall_precision, per_cost_result.values()):
            xs.append(x)
            ys.append(y)
        if not isinstance(args, str_type):
            args = ' '.join(args)
        plt.plot(xs, ys, 'o', label=args)
    plt.legend(loc='best')
    plt.grid(True)
    return fig

def make_tpr_fpr_plot(results):
    """
    ``results`` should be the result of `midas.see5.main`
    """
    fig = plt.figure()
    ax = fig.add_subplot('111')
    ax.set_ylabel('True Positive Rate')
    ax.set_xlabel('False Positive Rate')
    for args, per_cost_result in results.items():
        xs = []
        ys = []
        for confusion_matrix in per_cost_result.values():
            xs.append(calculate_fpr(confusion_matrix))
            ys.append(calculate_tpr(confusion_matrix))
        if not isinstance(args, str_type):
            args = ' '.join(args)
        plt.plot(xs, ys, 'o', label=args)
    plt.legend(loc='best')
    plt.grid(True)
    plt.plot([0.0, 0.5, 1.0], [0.0, 0.5, 1.0], 'k')
    return fig
