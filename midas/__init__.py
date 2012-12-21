# -*- coding: utf-8 -*-
""" Common functions that are needed in most other submodules.
"""

import datetime

#: The standard format we use to produce and parse time-stamps.
TS_FORMAT = '%Y-%m-%d'

def parse_tstamp(s, fmt=TS_FORMAT):
    return datetime.datetime.strptime(s, fmt)

def serialize_tstamp(tstamp, fmt=TS_FORMAT):
    return tstamp.strftime(fmt)
