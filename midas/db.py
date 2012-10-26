# -*- coding: utf-8 -*-
""" Provides functions and classes related to database access. It also
provides some common queries and filter conditions.
"""

import sqlalchemy as sa

import crawlcrunch.model.db as ccdb

import midas.config as md_cfg

_session = None

def db_session(db=None):
    """ Create a session for the CrunchBase database and return
    it. Subsequent calls will return the same session.
    """
    global _session
    if _session is None:
        if db is None:
            db = md_cfg.get('location', 'crunchbase_db')
        import midas.associate  # Get further table definitions
        engine = ccdb.create_engine(db)
        ccdb.Session.configure(bind=engine)
        ccdb.Base.metadata.create_all(engine)
        _session = ccdb.Session()
    return _session

p_fr_after_dec_2010 = sa.or_(
    ccdb.FundingRound.funded_year > 2010,
    sa.and_(
        ccdb.FundingRound.funded_year == 2010,
        ccdb.FundingRound.funded_month == 12
        )
    )

p_fr_in_a_angel_seed = ccdb.FundingRound.round_code.in_(
    ['angel', 'seed', 'a']
    )

p_c_has_hp_url = sa.and_(
    ccdb.Company.homepage_url != None,
    ccdb.Company.homepage_url != ''
    )

def q_fr_of_interest():
    """ Return a query for all funding rounds since December 2010 with
    `round_level` set to either ``angel``, ``seed`` or ``a``.
    """
    return db_session().query(ccdb.FundingRound)\
        .filter(p_fr_in_a_angel_seed)\
        .filter(p_fr_after_dec_2010)

def q_c_w_hp_url():
    """ Return a query for all the companies with a homepage URL.
    """
    return db_session().query(ccdb.Company)\
        .filter(p_c_has_hp_url)
