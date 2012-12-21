# -*- coding: utf-8 -*-

import os.path

_here = os.path.abspath(os.path.dirname(__file__))
_test_data_home = os.path.join(_here, '..', '..', 'test_data')

TEST_DATA_PATH = {
    'alexa_zip_files': os.path.join(_test_data_home, 'alexa_zip_files'),
    'alexa_files': os.path.join(_test_data_home, 'alexa_files'),
    }
