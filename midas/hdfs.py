# -*- coding: utf-8 -*-

import logging

from midas.tools import log_popen

import midas.config as md_cfg

logger = logging.getLogger(__name__)

def get_hadoop_exec():
    return md_cfg.get('hadoop', 'exec')

def put(file_or_files, dst):
    """ Put `files` to HDFS. `files` can either be a :class:`str` or a
    :class:`list` of :class:`str`.

    When a list of files is given try to be atomic: delete files
    already putted to HDFS when an error occurs.
    """
    if isinstance(file_or_files, list):
        copied = []
        for f in file_or_files:
            try:
                copied.append(put(f, dst))
            except:
                logger.critical('Removing copied files from HDFS.')
                for f in copied:
                    rm(f)
                raise
        return copied
    else:
        cmd = (get_hadoop_exec(), 'fs', '-put', file_or_files, dst)
        log_popen(cmd)
        return file_or_files

def rm(file_or_files):
    """ Remove `file_or_files` on HDFS. `file_or_files` can either be
    a :class:`str` or a :class:`list` of :class:`str`.
    """
    cmd = (get_hadoop_exec(), 'fs', '-rm', file_or_files, dst)
    log_popen(cmd)
