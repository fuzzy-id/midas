# -*- coding: utf-8 -*-

import os.path

class DestinationPaths(object):

    here = os.path.abspath(os.path.dirname(__file__))
    destinations = os.path.join(here, 'destinations')
    dl_complete = os.path.join(destinations, 'dl_complete')
