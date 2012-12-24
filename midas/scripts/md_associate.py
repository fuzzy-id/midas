# -*- coding: utf-8 -*-

from midas.compat import d_iteritems

import midas.associate as md_assoc
import midas.scripts as md_scripts

class MDAssociate(md_scripts.MDCommand):
    """ Populate the ``associations`` table.
    """

    def run(self):
        s2c = md_assoc.associate_companies_to_sites()
        for comp, sites in d_iteritems(s2c):
            for site in sites:
                print(','.join([comp.permalink, site]))
