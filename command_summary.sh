#!/bin/bash 
#
# Start this in an environment that is properly populated with the
# necessary tool set (i.e. Pig configuration, midas command set can be
# found in PATH, etc.).
#
ALEXA_ZIP_FILES="${ALEXA_ZIP_FILES:-/data1/alexa}"
INTERMEDIATE_DIR="${INTERMEDIATE_DIR:-/data0/run-midas-$(date +%F_%H-%m-%S)}"
