# -*- coding: utf-8 -*-
""" This module holds the result of some code that was usefull when
interacting with the data on the command line.
"""

def help_find_invalid_chars(company_name, line, column):  # pragma: no cover
    """ The CrunchBase API returns JSON which from time to time
    contains invalid characters. This is especially the case for the
    ``description`` field of comanies. These invalid characters raise
    an error in ``json.loads`` and should be replaced therefor. This
    happens in the ``CrunchBaseFetcherMixin`` class.

    Anyway, the name of the company, the line and the column as raised
    by ``json.loads`` can be fed in this function in order to examine
    them.
    """
    from crawlcrunch.compat import url_open
    from crawlcrunch.model import LocalFilesDir
    from crawlcrunch.model import CrunchBaseFetcherMixin
    root = LocalFilesDir('/tmp')
    company = root.get(company_name)
    resp = url_open(company.query_url())
    s = resp.read().decode('utf-8')
    s = CrunchBaseFetcherMixin.replace_control_chars(s)
    splitted = s.split('\n')
    l = splitted[line - 1]
    c = l[column - g1]
    print('The entire line is:\n{0!r}'.format(l))
    print('The specific character is: {0!r}'.format(c))
    return l, c
