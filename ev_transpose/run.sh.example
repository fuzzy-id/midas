#!/bin/bash

INPUT="input/infile"
OUT="out"

FILES="hdfs://localhost:9000/user/thbach/top-1m#data"


MAPPER="${HOME}/py_envs/cc26/bin/ev_tp_mapper"
REDUCER="${HOME}/.virtualenvs/py32/bin/ev_tp_reducer"
HADOOP_HOME="${HOME}/opt/hadoop-1.0.3"
HADOOP_BIN="${HADOOP_HOME}/bin/hadoop"
HADOOP_STREAMING="${HADOOP_HOME}/contrib/streaming/hadoop-streaming-1.0.3.jar"

${HADOOP_BIN} fs -rmr ${OUT}

${HADOOP_BIN} jar ${HADOOP_STREAMING} \
    -D mapred.map.tasks=6 \
    -D mapred.reduce.tasks=0 \
    -files ${FILES} \
    -input ${INPUT} \
    -output ${OUT} \
    -mapper ${MAPPER}
