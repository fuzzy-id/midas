# -*- coding: utf-8 -*-

from crawlcrunch.tests import unittest

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

    def _make_company(self, data):
        from crawlcrunch.model.local_files import ZippedJsonFile
        local_data = ZippedJsonFile('foo')
        local_data.data = data
        from crawlcrunch.model.local_files import Company as LocalCompany
        local = LocalCompany(local_data, 'dummy')

    def test_company_creation(self):
        from crawlcrunch.model.helper import local_file_company_to_db_model
        result = local_file_company_to_db_model(COMPANY_DATA)
        from crawlcrunch.model.db import Company
        from crawlcrunch.model.db import FundingRound
        self.assertIsInstance(result, Company)
        self.assertIsInstance(result.funding_rounds[0], FundingRound)
        self.assertEqual(result.updated_at, 'today')
