# -*- coding: utf-8 -*-
""" This module provides collected information on the different types
returned by the crunchbase API.
"""

# This is the main dict returned when querying for a company
def c(company):
    return company.data
COMPANY = {'acquisition': dict,
           'acquisitions': list,
           'alias_list': str,
           'blog_feed_url': str,
           'blog_url': str,
           'category_code': str,
           'competitions': list,
           'created_at': str,
           'crunchbase_url': str,
           'deadpooled_day': int,
           'deadpooled_month': int,
           'deadpooled_url': str,
           'deadpooled_year': int,
           'description': str,
           'email_address': str,
           'external_links': list,
           'founded_day': int,
           'founded_month': int,
           'founded_year': int,
           'funding_rounds': list,
           'homepage_url': str,
           'image': dict,
           'investments': list,
           'ipo': dict,
           'milestones': list,
           'name': str,
           'number_of_employees': int,
           'offices': list,
           'overview': str,
           'permalink': str,
           'phone_number': str,
           'products': list,
           'providerships': list,
           'relationships': list,
           'screenshots': list,
           'tag_list': str,
           'total_money_raised': str,
           'twitter_username': str,
           'updated_at': str,
           'video_embeds': list}

# acquisition 
def c_acquisition(company):
    return company.data['acquisition']
ACQUISITION = {'acquired_day': int,
               'acquired_month': int,
               'acquired_year': int,
               'acquiring_company': dict,
               'price_amount': float,
               'price_currency_code': str,
               'source_description': str,
               'source_url': str,
               'term_code': str}

# acquisitions -> acquiring_company
def c_acquisitions_acquiring_company(company):
    if company.data['acquisition'] is not None:
        return company.data['acquisition']['acquiring_company']
ACQUISITIONS_ACQUIRING_COMPANY = {'image': dict, # the same as image further down
                                  'name': str,
                                  'permalink': str}

# acquisitions
def c_acquisitions(company):
    return company.data['acquisitions']
ACQUISITIONS=[dict]

def c_acquisitions_d(company):
    if company.data['acquisitions'] is not None:
        return company.data['acquisitions'][0]

# image
def c_image(company):
    return company.data['image']
IMAGE = {'attribution': None, 
         'available_sizes': list}

# ipo
def c_ipo(company):
    return company.data['ipo']
IPO = {'pub_day': int,
       'pub_month': int,
       'pub_year': int,
       'stock_symbol': str,
       'valuation_amount': float,
       'valuation_currency_code': str}
