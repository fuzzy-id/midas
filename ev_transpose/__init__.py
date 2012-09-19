# -*- coding: utf-8 -*-

import collections

TP_TSTAMP_FORMAT = '%Y-%m-%d'
Entry = collections.namedtuple('Entry', ['name', 'date', 'rank'])
