# -*- coding: utf-8 -*-
import operator

def top_items(iterable, keyfunc, n=10, highest=True):
    top = []
    for item in iterable:
        t = (keyfunc(item), item)
        top.append(t)
    top.sort(reverse=highest)
    return top[:n]
