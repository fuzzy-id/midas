# -*- coding: utf-8 -*-

import os.path

class DestinationPaths(object):

    here = os.path.abspath(os.path.dirname(__file__))
    destinations = os.path.join(here, 'destinations')
    companies_empty = os.path.join(destinations, 'companies_empty')
    no_companies = os.path.join(destinations, 'no_companies')
