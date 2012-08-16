# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
Session = sessionmaker()


class Company(Base):
    __tablename__ = 'companies'

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
    updated_at = Column(String)
    funding_rounds = relationship('FundingRound', 
                                  backref='user')
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


class FundingRound(Base):
    __tablename__ = 'funding_rounds'
    
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
