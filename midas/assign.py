# -*- coding: utf-8 -*-
"""
Assigns the names found in top1m data an entry in the CrunchBase data.
"""

import sys

def find_strange_names():
    """ Finds names which have special characters in their names.  Can
    run in Hadoop.
    """
    norm_chars = set( chr(i) for i in range(ord('a'), ord('z') + 1) )
    norm_chars.update( chr(i) for i in range(ord('A'), ord('Z') + 1) )
    norm_chars.update( str(i) for i in range(0, 10) )
    norm_chars.add('.')
    last_processed = ''
    for line in sys.stdin:
        name, tail = line.split('\t')
        if last_processed != name:
            last_processed = name
            for c in name:
                if c not in norm_chars:
                    print(name)
                    break
    return 0
