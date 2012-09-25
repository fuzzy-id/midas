# -*- coding: utf-8 -*-

from midas import RankEntry
from midas.compat import GzipFile

def lookup_ranking(name, key_dir):
    key = RankEntry.make_key(name)
    fname = os.path.join(name, key_dir)
    entries = []
    with GzipFile(fname) as fp:
        for line in fp:
            entry = RankEntry.parse_key(line)
            if entry.name == name:
                entries.append(entry)
    return entries
