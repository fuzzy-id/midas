# -*- coding: utf-8 -*-

import threading

class Crawler(threading.Thread):

    def __init__(self, companies_list):
        super(Crawler, self).__init__()
        self.companies = companies_list

    def run(self):
        pass

