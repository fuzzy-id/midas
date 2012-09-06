# -*- coding: utf-8 -*-

import os.path

__here__ = os.path.abspath(os.path.dirname(__file__))
__test_data__ = os.path.join(__here__, 'data')
TEST_DATA = (
    (os.path.join(__test_data__, 'top-1m-2012-09-03.csv.zip', ),
     {'foo.csv.zip': '2012-09-03, 1',
      'bar.csv.zip': '2012-09-03, 2'}), )
