#!/bin/sh

home="/home/thomasba"

. ${home}/py_envs/py26_sys/bin/activate
MPLCONFIGDIR="${home}/.matplotlib"
export MPLCONFIGDIR

if [ -z "${PYTHONPATH}" ]; then
    PYTHONPATH="."
else
    PYTHONPATH=".:${PYTHONPATH}"
fi
export PYTHONPATH

exec $@