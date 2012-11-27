# -*- coding: utf-8 -*-
""" Provides functions and classes related to database access. It also
provides some common queries and filter conditions.
"""

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from crawlcrunch.model.db import Base
from crawlcrunch.model.db import Company
from crawlcrunch.model.db import FundingRound
from crawlcrunch.model.db import Session
from crawlcrunch.model.db import create_engine

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
        engine = create_engine(db)
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        _session = Session()
    return _session

class Association(Base):
    __tablename__ = 'associations'

    id = sa.Column(sa.Integer, primary_key=True)
    company_id = sa.Column(sa.Integer, sa.ForeignKey('companies.id'))
    site = sa.Column(sa.String)
    data_set = sa.Column(sa.Enum('test', 'training', name='data_type'))
    company = sa_orm.relationship("Company",
                                  backref=sa_orm.backref('site', 
                                                         uselist=False),
                                  lazy='subquery')

p_fr_after_mar_2011 = sa.and_(
    sa.or_(
        FundingRound.funded_year > 2011,
        sa.and_(
            FundingRound.funded_year == 2011,
            FundingRound.funded_month >= 3
            )
        ),
    FundingRound.funded_month != None,
    FundingRound.funded_day != None
    )

p_fr_in_a_angel_seed = FundingRound.round_code.in_(
    ['angel', 'seed', 'a']
    )

p_c_has_hp_url = sa.and_(
    Company.homepage_url != None,
    Company.homepage_url != ''
    )

def q_fr_of_interest():
    """ Return a query for all funding rounds since December 2010 with
    `round_level` set to either ``angel``, ``seed`` or ``a``.
    """
    return db_session().query(FundingRound)\
        .filter(p_fr_in_a_angel_seed)\
        .filter(p_fr_after_mar_2011)

def q_c_w_hp_url():
    """ Return a query for all the companies with a homepage URL.
8    """
    return db_session().query(Company)\
        .filter(p_c_has_hp_url)

def iter_sites_in_associations():
    """ Return all sites that can be found in the ``associations``
    table.
    """
    for site in db_session().query(Association.site).all():
        yield site[0]

def iter_all_companies():
    " Returns 100355 companies. "
    return db_session().query(Company).all()

def iter_interesting_companies():
    """ Returns all companies having a funding round with
    `round_level` ``angel``, ``seed`` or ``a`` since December 2010.
    """
    q = q_c_w_hp_url().join(q_fr_of_interest().subquery())
    return q.all()

