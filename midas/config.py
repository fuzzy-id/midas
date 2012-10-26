# -*- coding: utf-8 -*-
""" This module provides a :class:`configparser.ConfigParser` instance
as a singleton and functions to query this instance. Actually this is
an :class:`vincetools.compat.ConfigParser` instance. But, in most of
the cases this does not matter much.
"""

import logging
import logging.config
import os

from vincetools.compat import ConfigParser
from vincetools.compat import StringIO

logger = logging.getLogger(__name__)

#: The default configuration
DEFAULT_CONFIG = """
[DEFAULT]
user_name = {env[USER]}
hdfs_home = hdfs://localhost:9000/user/%(user_name)s
local_home = {env[HOME]}
virt_env = %(local_home)s/py_envs/py26

[job]
mapper = /path/to/mapper
num_mappers = 16
reducer = /path/to/reducer
num_reducers = 28
input = /path/to/input
output = optional
compress_output = true
files = optional

[location]
top1m_files = %(hdfs_home)s/alexa_files#alexa_files
key_length = 3
home = %(local_home)s/md_data
key_files = %(home)s/key_files
crunchbase_db = sqlite:///%(home)s/crunchbase_db.sql
site_count = %(home)s/site_count.gz

[hadoop]
home = %(local_home)s/opt/hadoop-1.0.3
exec = %(home)s/bin/hadoop
streaming = %(home)s/contrib/streaming/hadoop-streaming-1.0.3.jar

[loggers]
keys = root

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = DEBUG
handlers = console

[handler_console]
class = StreamHandler
args = (sys.stderr, )
level = INFO
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s %(message)s
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

def getboolean(section, option):
    """ Get an option value as :class:`bool` for a given section from
    the current :class:`configparser.ConfigParser` instance.
    """
    return get_configparser().getboolean(section, option)

def configure_logging():
    """ Configure logging by passing the configuration of the current
    :class:`configparser.ConfigParser` instance to
    :mod:`logging.config`.
    """
    buf = StringIO()
    get_configparser().write(buf)
    buf.seek(0)
    logging.config.fileConfig(buf, disable_existing_loggers=False)
