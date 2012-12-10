# -*- coding: utf-8 -*-

import numpy
import matplotlib.pyplot as plt

def get_available_days_before_fr(ts, fr):
    site, date, code = fr
    date = pandas.Timestamp(date)
    ts_site = ts[site].dropna()
    return code, (ts_site.index[0] - date).days

def make_available_days_before_funding_rounds_plot(data):
    arr = [numpy.array(data[key]) for key in ('seed', 'angel', 'a')]
    fig = plt.figure()
    ax = fig.add_subplot('111')
    res = ax.hist(arr, bins=20, histtype='bar', label=['Seed', 'Angel', 'A'])

    plt.ylim((0, 400))
    ax.annotate(' 1205', xy=(29, 390), xycoords='data', 
                xytext=(10, -20), textcoords='offset points', 
                arrowprops=dict(facecolor='blue'),
                horizontalalignment='left', verticalalignment='top')
    ax.legend()
    plt.title('Available Days before Funding Round')
    plt.ylabel('Number of Funding Rounds')
    plt.xlabel('Number of Days')
    plt.grid(True)
    plt.savefig('av_days_bef_fr.png')

def get_median_rank(ts, fr, start, end):
    site, date, code = fr
    ts_site = ts[site][(date + start):(date + end)].dropna()
    return code, ts_site.median()

def median_rank_before_funding(ts, frs, start_days, end_days):
    data = collections.defaultdict(list)
    start = datetime.timedelta(days=start_days)
    end = datetime.timedelta(days=end_days)
    for fr in frs:
        site, date, code = fr
        code, rank = get_median_rank(ts, fr, start, end)
        if rank > 0:  # Filter out NaN's
            data[code].append(rank)
    return data

def make_rank_before_funding_plot(data, title, keys=('seed', 'angel', 'a'), **kwargs):
    arr = [ numpy.array(data[key]) for key in keys ]
    fig = plt.figure()
    ax = fig.add_subplot('111')
    res = ax.hist(arr, label=['Seed', 'Angel', 'A'], **kwargs)
    plt.legend(loc='best')
    plt.grid(True)
    plt.title(title)
    plt.xlabel('Rank')
    plt.ylabel('Number of Funding Rounds')
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
