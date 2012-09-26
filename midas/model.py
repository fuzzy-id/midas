# -*- coding: utf-8 -*-

import itertools
import os.path

from midas import RankEntry
from midas.compat import GzipFile

def lookup_ranking(name, key_dir):
    key = RankEntry.make_key(name)
    fname = os.path.join(key_dir, '{0}.gz'.format(key))
    entries = []
    with GzipFile(fname) as fp:
        pred = lambda l: RankEntry.parse_std(l.decode()).name != name
        for line in itertools.dropwhile(pred, fp):
            entry = RankEntry.parse_std(line.decode())
            if entry.name == name:
                yield entry
            else:
                break
