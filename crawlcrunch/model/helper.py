# -*- coding: utf-8 -*-
""" This module holds the result of some code that was usefull when
interacting with the data on the command line.
"""

from crawlcrunch.model.db import Company
from crawlcrunch.model.db import FundingRound

def help_find_invalid_chars(company_name, line, column):  # pragma: no cover
    """ The CrunchBase API returns JSON which from time to time
    contains invalid characters. This is especially the case for the
    ``description`` field of comanies. These invalid characters raise
    an error in ``json.loads`` and should be replaced therefor. This
    happens in the ``CrunchBaseFetcherMixin`` class.

    Anyway, the name of the company, the line and the column as raised
    by ``json.loads`` can be fed in this function in order to examine
    them.
    """
    from crawlcrunch.compat import url_open
    from crawlcrunch.model import LocalFilesDir
    from crawlcrunch.model import CrunchBaseFetcherMixin
    root = LocalFilesDir('/tmp')
    company = root.get(company_name)
    resp = url_open(company.query_url())
    s = resp.read().decode('utf-8')
    s = CrunchBaseFetcherMixin.replace_control_chars(s)
    splitted = s.split('\n')
    l = splitted[line - 1]
    c = l[column - g1]
    print('The entire line is:\n{0!r}'.format(l))
    print('The specific character is: {0!r}'.format(c))
    return l, c

def local_file_company_to_db_model(data):
    company_fields = ('alias_list',
                      'blog_feed_url',
                      'blog_url',
                      'category_code',
                      'created_at',
                      'crunchbase_url',
                      'deadpooled_day',
                      'deadpooled_month',
                      'deadpooled_url',
                      'deadpooled_year',
                      'description',
                      'email_address',
                      'founded_day',
                      'founded_month',
                      'founded_year',
                      'homepage_url',
                      'name',
                      'number_of_employees',
                      'overview',
                      'permalink',
                      'phone_number',
                      'tag_list',
                      'total_money_raised',
                      'twitter_username',
                      'updated_at')
    funding_fields = ('funded_day',
                      'funded_month',
                      'funded_year',
                      'raised_amount',
                      'raised_currency_code',
                      'round_code',
                      'source_description',
                      'source_url')
    funding_rounds = []
    for funding in data.get('funding_rounds', []):
        d = dict(((k, funding[k]) for k in funding_fields))
        funding_rounds.append(FundingRound(**d))
    d = dict(((k, data[k]) for k in company_fields))
    d['funding_rounds'] = funding_rounds
    return Company(**d)


def push_companies_from_files_to_db(companies, root, session):  # pragma: no cover
    for company_name in companies:
        company = root.get(company_name)
        company.load()  # this never hurts as data is cached
        db_company = local_file_company_to_db_model(company.local_data.data)
        session.add(db_company)
