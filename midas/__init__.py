# -*- coding: utf-8 -*-

import collections

Entry = collections.namedtuple('Entry', ['name', 'date', 'rank'])

class Entry(object):

    TS_FORMAT = '%Y-%m-%d'

    def __init__(name, date, rank):
        self.name = name
        self.date = date
        self.rank = rank

    def __str__(self):
        " The standard format. "
        date = datetime.strftime(self.date, TS_FORMAT)
        return '{e.name}\t{0}, {e.rank}'.format(date, e=self)
