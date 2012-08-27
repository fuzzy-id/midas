# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
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

TM_FORMAT = '%a %b %d %H:%M:%S %Z %Y'

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
    updated_at = Column(DateTime)

    funding_rounds = relationship('FundingRound', 
                                  backref='company')
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

    @classmethod
    def make_from_parsed_json(cls, parsed_json):
        fundings = []
        for funding in parsed_json.get('funding_rounds', []):
            d = FundingRound.make_from_parsed_json(funding)
            fundings.append(d)
        fields = ( f.name for f in cls.__table__.columns
                   if f.name != 'id' )
        d = dict(((field, parsed_json.get(field, None)) 
                  for field in fields))
        if d.get('updated_at', None) is not None:
            d['updated_at'] = datetime.strptime(d['updated_at'],
                                                TM_FORMAT)
        d['funding_rounds'] = fundings
        return cls(**d)


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

    @classmethod
    def make_from_parsed_json(cls, parsed_json):
        fields = ( f.name for f in cls.__table__.columns
                   if f.name != 'id' and f.name != 'company_id' )
        d = dict(((field, parsed_json.get(field, None)) 
                  for field in fields))
        return cls(**d)
        
