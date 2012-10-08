# -*- coding: utf-8 -*-

import logging
import os

from midas.compat import ConfigParser
from midas.compat import StringIO

logger = logging.getLogger(__name__)

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

[alexa]
top1m_files = %(hdfs_home)s/alexa-files#alexa-files
key_length = 3

[statistics]
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
    cp = ConfigParser()
    cp.read_string(DEFAULT_CONFIG)
    global _configparser
    _configparser = cp

new_configparser()

def read(files):
    """ Read configuration from `files` into the modules
    :class:`configparser.ConfigParser` instance.
    """
    get_configparser().read(files)

def configure_logging():
    buf = StringIO()
    get_configparser().write(buf)
    buf.seek(0)
    logging.config.fileConfig(buf)

def set(sect, opt, val):
    return get_configparser().set(sect, opt, val)

def get(sect, opt):
    return get_configparser().get(sect, opt)

def getint(sect, opt):
    return get_configparser().getint(sect, opt)

def getboolean(sect, opt):
    return get_configparser().getboolean(sect, opt)

def get_configparser():
    return _configparser
