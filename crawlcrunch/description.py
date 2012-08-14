# -*- coding: utf-8 -*-
""" This module provides collected information on the different types
returned by the crunchbase API.
"""

# This is the main dict returned when querying for a company
def access_company(company):
    return company.data

COMPANY = {u'acquisition': dict,
           u'acquisitions': list,
           u'alias_list': str,
           u'blog_feed_url': str,
           u'blog_url': str,
           u'category_code': str,
           u'competitions': list,
           u'created_at': str,
           u'crunchbase_url': str,
           u'deadpooled_day': int,
           u'deadpooled_month': int,
           u'deadpooled_url': str,
           u'deadpooled_year': int,
           u'description': str,
           u'email_address': str,
           u'external_links': list,
           u'founded_day': int,
           u'founded_month': int,
           u'founded_year': int,
           u'funding_rounds': list,
           u'homepage_url': str,
           u'image': dict,
           u'investments': list,
           u'ipo': dict,
           u'milestones': list,
           u'name': str,
           u'number_of_employees': int,
           u'offices': list,
           u'overview': str,
           u'permalink': str,
           u'phone_number': str,
           u'products': list,
           u'providerships': list,
           u'relationships': list,
           u'screenshots': list,
           u'tag_list': str,
           u'total_money_raised': str,
           u'twitter_username': str,
           u'updated_at': str,
           u'video_embeds': list}

# acquisition 
def access_company_acquisition(company):
    return company.data['acquisition']
ACQUISITION = {u'acquired_day': int,
               u'acquired_month': int,
               u'acquired_year': int,
               u'acquiring_company': dict,
               u'price_amount': float,
               u'price_currency_code': str,
               u'source_description': str,
               u'source_url': str,
               u'term_code': str}

# acquisitions
def access_company_acquisitions(company):
    return company.data['acquisitions']
