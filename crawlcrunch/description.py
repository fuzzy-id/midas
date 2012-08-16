# -*- coding: utf-8 -*-
""" This module provides collected information on the different types
returned by the crunchbase API.
"""

from crawlcrunch.helper import Model


def make_root_acces(root):
    def access_func(company_name):
        company = root.get(company_name)
        return company.data
    return access_func

IMAGE = Model({'attribution': None,
               'available_sizes': list})
# TODO: this is not resolved properly:
IMAGE.available_sizes = Model([list, list, list])

COMPANY = Model({'permalink': str,
                 'name': str,
                 'image': dict})
COMPANY.image = IMAGE

PERSON = Model({'first_name': str,
                'image': dict,
                'last_name': str,
                'permalink': str})
PERSON.image = IMAGE

ROOT = Model({'acquisition': dict,
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
              'video_embeds': list})

ROOT.acquisition = Model(
    {'acquired_day': int,
     'acquired_month': int,
     'acquired_year': int,
     'acquiring_company': dict,
     'price_amount': float,
     'price_currency_code': str,
     'source_description': str,
     'source_url': str,
     'term_code': str})
ROOT.acquisition.acquiring_company = COMPANY

ROOT.acquisitions = Model([dict])
ROOT.acquisitions.list = Model(
    {'acquired_day': int,
     'acquired_month': int,
     'acquired_year': int,
     'company': dict,
     'price_amount': float,
     'price_currency_code': str,
     'source_description': str,
     'source_url': str,
     'term_code': str})
ROOT.acquisitions.list.company = COMPANY

ROOT.competitions = Model([dict])
ROOT.competitions.list = Model(
    {'competitor': dict})
ROOT.competitions.list.competitor = COMPANY

ROOT.external_links = Model([dict])
ROOT.external_links.list = Model(
    {'external_url': str,
     'title': str})

ROOT.funding_rounds = Model([dict])
ROOT.funding_rounds.list = Model(
    {'funded_day': int,
     'funded_month': int,
     'funded_year': int,
     'investments': list,
     'raised_amount': float,
     'raised_currency_code': str,
     'round_code': str,
     'source_description': str,
     'source_url': str})

ROOT.funding_rounds.list.investments = Model([dict])
ROOT.funding_rounds.list.investments.list = Model(
    {'company': dict,
     'financial_org': dict,
     'person': dict})
ROOT.funding_rounds.list.investments.list.company = COMPANY
ROOT.funding_rounds.list.investments.list.financial_org = COMPANY
ROOT.funding_rounds.list.investments.list.person = PERSON

ROOT.image = IMAGE
ROOT.investments = Model([dict])
ROOT.investments.list = Model(
    {'funding_round': dict})

ROOT.investments.list.funding_round = Model(
    {'company': dict,
     'funded_day': int,
     'funded_month': int,
     'funded_year': int,
     'raised_amount': float,
     'raised_currency_code': str,
     'round_code': str,
     'source_description': str,
     'source_url': str})
ROOT.investments.list.funding_round.company = COMPANY

ROOT.ipo = Model(
    {'pub_day': int,
     'pub_month': int,
     'pub_year': int,
     'stock_symbol': str,
     'valuation_amount': float,
     'valuation_currency_code': str})

ROOT.milestones = Model([dict])
ROOT.milestones.list = Model(
    {'description': str,
     'source_description': str,
     'source_text': str,
     'source_url': str,
     'stoneable': dict,
     'stoneable_type': str,
     'stoned_acquirer': None,
     'stoned_day': int,
     'stoned_month': int,
     'stoned_value': None,
     'stoned_value_type': None,
     'stoned_year': int})
ROOT.milestones.list.stoneable = Model(
    {'permalink': str,
     'name': str})

ROOT.offices = Model([dict])
ROOT.offices.list = Model({'address1': str,
                           'address2': str,
                           'city': str,
                           'country_code': str,
                           'description': str,
                           'latitude': float,
                           'longitude': float,
                           'state_code': str,
                           'zip_code': str})

ROOT.products = Model([dict])
ROOT.products.list = Model(
    {'image': dict,
     'name': str,
     'permalink': str})
ROOT.products.list.image = IMAGE

ROOT.providerships = Model([dict])
ROOT.providerships.list = Model(
    {'is_past': int,
     'provider': dict,
     'title': str})

ROOT.providerships.list.provider = COMPANY

ROOT.relationships = Model([dict])
ROOT.relationships.list = Model({'is_past': int,
                                 'person': dict,
                                 'title': str})
ROOT.relationships.list.person = PERSON

ROOT.screenshots = Model([dict])
ROOT.screenshots.list = IMAGE

ROOT.screenshots.video_embeds = Model([dict])
ROOT.screenshots.video_embeds.list = Model(
    {'embed_code': str,
     'description': str})
