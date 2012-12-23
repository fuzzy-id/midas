#!/bin/sh

. /home/thomasba/py_envs/py26_sys/bin/activate
MPLCONFIGDIR="/home/thomasba/.matplotlib"
export MPLCONFIGDIR

if [ -z ${PYTHONPATH} ]; then
    PYTHONPATH="."
else
    PYTHONPATH=".:${PYTHONPATH}"
fi
export PYTHONPATH

python $@