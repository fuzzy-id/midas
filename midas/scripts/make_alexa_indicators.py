# -*- coding: utf-8 -*-

import itertools

from midas.compat import d_iteritems
from midas.scripts import MDCommand

FILTERS = set(['rsi', 'ols-slope', 'spearman', 'pearson' 'rank'])

def expand_config(conf):
    for filter_, args in d_iteritems(conf):
        if not filter_ in FILTERS:
            raise ValueError('Unknown filter: {0}'.format(filter_))
        ndays = args['ndays']
        thresholds = args['thresholds']
        if isinstance(ndays, dict):
            ndays = xrange(ndays['start'], ndays['stop'], ndays['step'])
        if isinstance(thresholds, dict):
            thresholds = xrange(thresholds['start'], 
                                thresholds['stop'], 
                                thresholds.get('step', 1))
        for days, threshold in itertools.product(ndays, thresholds):
            yield (filter_, days, threshold)
            

class MakeAlexaIndicators(MDCommand):
    pass
