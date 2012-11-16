# -*- coding: utf-8 -*-

import vincetools.compat as vt_comp

import midas.associate as md_assoc
import midas.db as md_db
import midas.scripts as md_scripts

class MDAssociate(md_scripts.MDCommand):
    """ Populate the ``associations`` table.
    """

    def run(self):
        s2c = md_assoc.associate_companies_to_sites()
        sess = md_db.db_session()
        for comp, sites in vt_comp.d_iteritems(s2c):
            for site in sites:
                association = md_db.Association(company=comp, site=site)
                sess.add(association)
        sess.commit()
