# -*- coding: utf-8 -*-

from datetime import datetime

import logging
import threading

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound

from crawlcrunch.model import CrunchBaseFetcherMixin

Base = declarative_base()
Session = scoped_session(sessionmaker())

DB_LOCK = threading.RLock()

TM_FORMAT = '%a %b %d %H:%M:%S %Z %Y'

class DataBaseRoot(object):

    def __init__(self, db_path):
        self.db_path = db_path
        engine = create_engine(db_path)
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)

    def get(self, name):
        if name == 'companies':
            return CompanyList()
        raise ValueError("No such class '{0}'".format(name))

    def clean_up(self):
        Session.remove()


class CompanyList(CrunchBaseFetcherMixin):

    def __init__(self):
        self._remote_data = None

    def list_local(self):
        session = Session()
        q = session.query(Company)
        with DB_LOCK:
            companies = q.all()
        for company in companies:
            yield company

    def list_not_local(self):
        remotes = set( entry['permalink'] for entry in self._remote_data )
        locals_ = set( c.permalink for c in self.list_local() )
        not_locals = remotes - locals_
        for permalink in not_locals:
            yield Company(permalink=permalink)

    def get(self, permalink):
        session = Session()
        q = session.query(Company).filter(Company.permalink == permalink)
        try:
            with DB_LOCK:
                return q.one()
        except NoResultFound as e:
            return Company(permalink=permalink)
        except MultipleResultsFound as e:
            logging.critical(
                "Exception raised when processing: '{0}'".format(permalink))
            raise e

    def update(self):
        self._remote_data = self.fetch()

    def query_url(self):
        return self.companies_list_url

def make_from_parsed_json(cls, parsed_json):
    return cls(**dict((f.name, parsed_json.get(f.name, None)) 
                      for f in cls.__table__.columns
                      if f.name not in cls.special_fields ))

class Company(Base, CrunchBaseFetcherMixin):
    __tablename__ = 'companies'

    special_fields = set(('id'))

    id = Column(Integer, primary_key=True)
    alias_list = Column(String)
    blog_feed_url = Column(String)
    blog_url = Column(String)
    category_code = Column(String)
    created_at = Column(String)
    crunchbase_url = Column(String)
    deadpooled_day = Column(Integer)
    deadpooled_month = Column(Integer)
    deadpooled_url = Column(String)
    deadpooled_year = Column(Integer)
    description = Column(String)
    email_address = Column(String)
    founded_day = Column(Integer)
    founded_month = Column(Integer)
    founded_year = Column(Integer)
    homepage_url = Column(String)
    name = Column(String)
    number_of_employees = Column(Integer)
    overview = Column(String)
    permalink = Column(String)
    phone_number = Column(String)
    tag_list = Column(String)
    total_money_raised = Column(String)
    twitter_username = Column(String)
    updated_at = Column(DateTime)

    funding_rounds = relationship('FundingRound', 
                                  backref='company',
                                  cascade='all, delete, delete-orphan',
                                  lazy='subquery')
    external_links = relationship('ExternalLink', 
                                  backref='company',
                                  cascade='all, delete, delete-orphan',
                                  lazy='subquery')
    # 'acquisiton': dict,
    # 'acquisitions': list,
    # 'competitions': list,
    # 'external_links': list,
    # 'image': dict,
    # 'investments': list,
    # 'ipo': dict,
    # 'milestones': list,
    # 'offices': list,
    # 'products': list,
    # 'providerships': list,
    # 'relationships': list,
    # 'screenshots': list,
    # 'video_embeds': list

    def __str__(self):
        return 'Company({0})'.format(self.permalink)

    def __hash__(self):
        return hash(self.permalink)

    @classmethod
    def make_from_parsed_json(cls, parsed_json):
        obj = make_from_parsed_json(cls, parsed_json)
        if obj.updated_at:
            obj.updated_at = datetime.strptime(obj.updated_at,
                                               TM_FORMAT)
        for cls, field in ((FundingRound, 'funding_rounds'),
                           (ExternalLink, 'external_links')):
            if parsed_json.get(field):
                setattr(obj, field, [ make_from_parsed_json(cls, js)
                                      for js in parsed_json[field] ])
        return obj

    def update(self):
        data = self.fetch()
        new_c = self.make_from_parsed_json(data)
        if self.updated_at is None or new_c.updated_at > self.updated_at:
            logging.info('Updating {0}'.format(self))
            session = Session()
            if self.id is not None:
                session.delete(self)
            session.add(new_c)
            with DB_LOCK:
                session.commit()

    def query_url(self):
        return self.company_url_tpl.format(self.permalink)


class FundingRound(Base):
    __tablename__ = 'funding_rounds'

    special_fields = set(('id', 'company_id'))
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    funded_day = Column(Integer)
    funded_month = Column(Integer)
    funded_year = Column(Integer)
    raised_amount = Column(Float)
    raised_currency_code = Column(String)
    round_code = Column(String)
    source_description = Column(String)
    source_url = Column(String)
    # 'investments': list,


class ExternalLink(Base):
    __tablename__ = 'external_links'
    
    special_fields = set(('id', 'company_id'))

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    external_url = Column(String)
    title = Column(String)
