# -*- coding: utf-8 -*-

from midas.compat import unittest

COMPANY_DATA = {'acquisition': {},
                'acquisitions': [],
                'alias_list': 'aliases',
                'blog_feed_url': 'a url',
                'blog_url': 'another url',
                'category_code': 'categories',
                'competitions': [],
                'created_at': 'a data',
                'crunchbase_url': 'url',
                'deadpooled_day': 8,
                'deadpooled_month': 10,
                'deadpooled_url': 'one more url',
                'deadpooled_year': 2012,
                'description': 'a dummy company',
                'email_address': 'foo@example.com',
                'external_links': [],
                'founded_day': 12,
                'founded_month': 12,
                'founded_year': 109,
                'funding_rounds': [{'funded_day': 10,
                                    'funded_month': 20,
                                    'funded_year': 10,
                                    'investments': [],
                                    'raised_amount': 12.9,
                                    'raised_currency_code': 'USD',
                                    'round_code': 'angel',
                                    'source_description': 'blahblah',
                                    'source_url': 'an url'}],
                'homepage_url': 'fofo',
                'image': {},
                'investments': [],
                'ipo': {},
                'milestones': [],
                'name': 'dummy & co',
                'number_of_employees': 1,
                'offices': [],
                'overview': 'we provide dummies',
                'permalink': 'dummy',
                'phone_number': '808080',
                'products': [],
                'providerships': [],
                'relationships': [],
                'screenshots': [],
                'tag_list': 'dummies',
                'total_money_raised': '87',
                'twitter_username': 'dummy.twit',
                'updated_at': 'today',
                'video_embeds': []}

class LocalFileCompanyToDbModelTests(unittest.TestCase):

    def test_company_creation(self):
        from midas.crunchbase_crawler.model.helper import local_file_company_to_db_model
        from midas.crunchbase_crawler.model.db import Company
        from midas.crunchbase_crawler.model.db import FundingRound
        result = local_file_company_to_db_model(COMPANY_DATA)
        self.assertIsInstance(result, Company)
        self.assertIsInstance(result.funding_rounds[0], FundingRound)
        self.assertEqual(result.updated_at, 'today')
