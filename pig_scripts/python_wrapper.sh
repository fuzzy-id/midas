#!/bin/sh

. /home/thomasba/py_envs/py26_sys/bin/activate
MPLCONFIGDIR="/home/thomasba/.matplotlib"
export MPLCONFIGDIR

if [ -z $CLASSPATH ]; then
    CLASSPATH="."
else
    CLASSPATH=".:${CLASSPATH}"
fi
export CLASSPATH

python $@