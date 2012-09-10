#!/bin/bash

INPUT="input/infile"
OUT="out"

FILES="hdfs://localhost:9000/user/tbach/top-1m#data"


MAPPER="${HOME}/.virtualenvs/py32/bin/ev_tp_mapper"
REDUCER="${HOME}/.virtualenvs/py32/bin/ev_tp_reducer"
HADOOP_HOME="${HOME}/opt/hadoop-1.0.3"
HADOOP_BIN="${HADOOP_HOME}/bin/hadoop"
HADOOP_STREAMING="${HADOOP_HOME}/contrib/streaming/hadoop-streaming-1.0.3.jar"

${HADOOP_BIN} fs -rmr ${OUT}

${HADOOP_BIN} jar ${HADOOP_STREAMING} \
    -D mapred.map.tasks=3 \
    -D mapred.reduce.tasks=3 \
    -D mapred.output.compress=true \
    -D mapred.output.compression.codec=org.apache.hadoop.io.compress.GzipCodec \
    -files ${FILES} \
    -input ${INPUT} \
    -output ${OUT} \
    -mapper ${MAPPER} \
    -reducer ${REDUCER}
