# -*- coding: utf-8 -*-

from __future__ import print_function

import sys


def normalize_site(name):
    splits = name.split('/')
    if splits[0] == 'http:':
        assert splits[1] == ''
        host = splits[2]
    else:
        host = splits[0]
    splits = host.split('.')
    return '.'.join(splits[-2:])

