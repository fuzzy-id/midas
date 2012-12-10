# -*- coding: utf-8 -*-
""" This module provides a :class:`configparser.ConfigParser` instance
as a singleton and functions to query this instance. Actually this is
an :class:`vincetools.compat.ConfigParser` instance. But, in most of
the cases this does not matter much.
"""

import os

from midas.compat import ConfigParser
from midas.compat import StringIO

#: The default configuration
DEFAULT_CONFIG = """
[DEFAULT]
local_home = {env[HOME]}

[location]
data_home = %(local_home)s/md_data
alexa_zip_files = %(data_home)s/alexa_zip_files
alexa_files = %(data_home)s/alexa_files
site_count = %(data_home)s/site_count.gz
sites = %(data_home)s/sites.gz
crunchbase_db = sqlite:///%(data_home)s/crunchbase_db.sql
""".format(env=os.environ)

_configparser = None

def new_configparser():
    """ Generate a new :class:`configparser.ConfigParser` instance and
    configure it with the :attr:`DEFAULT_CONFIG`.
    """
    cp = ConfigParser()
    global _configparser
    _configparser = cp
    read_string(DEFAULT_CONFIG)

def read_string(s):
    get_configparser().read_string(s)

def get_configparser():
    """ Return the current :class:`configparser.ConfigParser`
    instance.
    """
    return _configparser

new_configparser()

def read(files):
    """ Read configuration from `files` into the modules
    :class:`configparser.ConfigParser` instance.
    """
    get_configparser().read(files)

def set(section, option, value):
    """ Set an option on the current
    :class:`configparser.ConfigParser` instance. 
    """
    return get_configparser().set(section, option, value)

def get(section, option):
    """ Get an option value for a given section from the current
    :class:`configparser.ConfigParser` instance.
    """
    return get_configparser().get(section, option)

def getint(section, option):
    """ Get an option value as :class:`int` for a given section from
    the current :class:`configparser.ConfigParser` instance.
    """
    return get_configparser().getint(section, option)
