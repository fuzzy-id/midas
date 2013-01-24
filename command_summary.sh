#!/bin/bash
#
# Start this in an environment that is properly populated with the
# necessary tool set (i.e. Pig configuration, midas command set can be
# found in PATH, etc.).
#

set -e
#
# The zipped Top 1M Alexa files as given by alexa.com
ALEXA_ZIP_FILES="${ALEXA_ZIP_FILES:-/data1/alexa}"
# A list of files that should be filtered out
ADULT_SITES="/data0/adult_sites"
# The file relating ids to sites
IDS_TO_SITES="/data0/ids_to_sites"
# The crawled data from CrunchBase
CRUNCHBASE_COMPANIES="/data0/crunchbase_companies"
INTERMEDIATE_DIR="${INTERMEDIATE_DIR:-/data0/run-midas-$(date +%F_%H-%M)}"
PIG_SCRIPTS="${PIG_SCRIPTS:-${HOME}/src/midas/pig_scripts}"
PIG_OPTIONS="-b"
#
# Set FETCH_COMPANIES to 'Y', when you want this script to run
# `md_fetch_crunchbase_companies'.
#
FETCH_COMPANIES="${FETCH_COMPANIES:-N}"

#########################################
## Internal Variables                  ##
##                                     ##
## You should not need to alter these. ##
#########################################
HADOOP_INTERMEDIATE_DIR="$(basename ${INTERMEDIATE_DIR})"

FETCH_COMPANIES_NUM_THREADS="5"
NEGATIVE_TO_POSITIVE_SAMPLES_RATIO="10"

MY_ADULT_SITES_FILE="adult_sites"
MY_ALEXA_FILES="alexa_files"
MY_ASSOCIATIONS="associations"
MY_COMPANIES="companies"
MY_CRUNCHBASE_COMPANIES="crunchbase_companies"
MY_IDS_TO_SITES="ids_to_sites"
MY_NEGATIVE_SAMPLES="samples_negative"
MY_POSITIVE_SAMPLES="samples_positive"
MY_RESTRICTIONS="restrictions"
MY_SHAPED_NEGATIVE_SAMPLES="samples_shaped_negative"
MY_SHAPED_POSITIVE_SAMPLES="samples_shaped_positive"
MY_SITES="sites"
MY_SITE_COUNT="site_count"
MY_SITES_W_COMPANY="sites_w_company"
MY_SITES_WO_COMPANY="sites_wo_company"
MY_SITES_WO_COMPANY_SPLITS="sites_wo_company_splitted"
MY_TSTAMP_TO_SECS="tstamp_to_secs"

set -x

if [ ! -d "${INTERMEDIATE_DIR}" ]; then
    mkdir "${INTERMEDIATE_DIR}"
fi

if ! hadoop fs -test -d "${HADOOP_INTERMEDIATE_DIR}"; then
    hadoop fs -mkdir "${HADOOP_INTERMEDIATE_DIR}"
fi

####################################################################
## Unzip Alexa Files and Push Date in CSV                         ##
##                                                                ##
## Dependencies:                                                  ##
##   + ALEXA_ZIP_FILES :: Top1M Alexa Files in Zip Format         ##
##                                                                ##
## Produces:                                                      ##
##   + ALEXA_FILES :: The same data, with the TSTAMP in the file  ##
##                                                                ##
####################################################################

if ! hadoop fs -test -d "${HADOOP_INTERMEDIATE_DIR}/${MY_ALEXA_FILES}"; then

    if [ ! -d "${INTERMEDIATE_DIR}/${MY_ALEXA_FILES}" ]; then
	mkdir "${INTERMEDIATE_DIR}/${MY_ALEXA_FILES}"
    fi

    md_unzip_alexa_files \
	"${ALEXA_ZIP_FILES}" \
	"${INTERMEDIATE_DIR}/${MY_ALEXA_FILES}"
    hadoop fs -put \
	"${INTERMEDIATE_DIR}/${MY_ALEXA_FILES}" \
	"${HADOOP_INTERMEDIATE_DIR}/${MY_ALEXA_FILES}"
fi

####################################################################
## Inverting the index                                            ##
##                                                                ##
## Dependencies:                                                  ##
##   + ALEXA_FILES                                                ##
##   + ADULT_SITES :: A list of sites that should be filtered out ##
##                                                                ##
## Produces:                                                      ##
##   + SITES :: Alexa Data Indexed by their site                  ##
##                                                                ##
####################################################################
if ! hadoop fs -test -e "${HADOOP_INTERMEDIATE_DIR}/${MY_SITES}"; then
    if ! hadoop fs -test -e "${HADOOP_INTERMEDIATE_DIR}/${MY_ADULT_SITES_FILE}"; then
	hadoop fs -put \
	    "${ADULT_SITES}" \
	    "${HADOOP_INTERMEDIATE_DIR}/${MY_ADULT_SITES_FILE}"
    fi

    pig ${PIG_OPTIONS} \
	-p alexa_files=${HADOOP_INTERMEDIATE_DIR}/${MY_ALEXA_FILES} \
	-p adult_sites=${HADOOP_INTERMEDIATE_DIR}/${MY_ADULT_SITES_FILE} \
	-p sites=${HADOOP_INTERMEDIATE_DIR}/${MY_SITES} \
	"${PIG_SCRIPTS}/group_alexa_by_site.pig"
fi

####################################################################
## Generating the site count                                      ##
##                                                                ##
## Dependencies:                                                  ##
##   + ALEXA_FILES                                                ##
## Produces:                                                      ##
##   + SITE_COUNT :: The number of available time points per site ##
##                                                                ##
####################################################################

pig ${PIG_OPTIONS} \
    -p sites=${HADOOP_INTERMEDIATE_DIR}/${MY_SITES} \
    -p site_count=${HADOOP_INTERMEDIATE_DIR}/${MY_SITE_COUNT} \
    "${PIG_SCRIPTS}/count_entries_per_site.pig"

#######################################################################
## Flatten and Filter the CrunchBase Data                            ##
##                                                                   ##
## Dependencies:                                                     ##
##   + CRUNCHBASE_COMPANIES :: The crawled companies from CrunchBase ##
## Produces:                                                         ##
##   + COMPANIES :: All companies providing a HP URL with the last   ##
##     funding event with round code A, Angels or Seed               ##
##                                                                   ##
#######################################################################

if [[ "${FETCH_COMPANIES}" == "Y" ]]; then
    md_fetch_crunchbase_companies \
	-p ${FETCH_COMPANIES_NUM_THREADS} \
	${CRUNCHBASE_COMPANIES}
fi

hadoop fs -put \
    ${CRUNCHBASE_COMPANIES} \
    ${HADOOP_INTERMEDIATE_DIR}/${MY_CRUNCHBASE_COMPANIES}
pig ${PIG_OPTIONS} \
    -p flatten_cmd=$(which md_flatten_companies) \
    -p crunchbase_companies=${HADOOP_INTERMEDIATE_DIR}/${MY_CRUNCHBASE_COMPANIES} \
    -p companies=${HADOOP_INTERMEDIATE_DIR}/${MY_COMPANIES} \
    ${PIG_SCRIPTS}/flatten_and_filter_companies.pig

###########################################################
## Generating Assocations                                ##
##                                                       ##
## Dependencies:                                         ##
##   + COMPANIES                                         ##
##   + SITE_COUNT                                        ##
## Produces:                                             ##
##   + ASSOCIATIONS :: A mapping from sites to companies ##
##                                                       ##
###########################################################

hadoop fs -get \
    ${HADOOP_INTERMEDIATE_DIR}/${MY_COMPANIES} \
    ${INTERMEDIATE_DIR}/${MY_COMPANIES}
hadoop fs -get \
    ${HADOOP_INTERMEDIATE_DIR}/${MY_SITE_COUNT} \
    ${INTERMEDIATE_DIR}/${MY_SITE_COUNT}
md_associate \
    ${INTERMEDIATE_DIR}/${MY_SITE_COUNT} \
    ${INTERMEDIATE_DIR}/${MY_COMPANIES} \
    > ${INTERMEDIATE_DIR}/${MY_ASSOCIATIONS}

#################################################################
## Joining Sites and Companies                                 ##
##                                                             ##
## Dependencies:                                               ##
##   + ASSOCIATIONS                                            ##
##   + SITES                                                   ##
##   + COMPANIES                                               ##
## Produces:                                                   ##
##   + SITES_W_COMPANY :: Sites with an associated Company     ##
##   + SITES_WO_COMPANY :: Sites without an associated Company ##
##                                                             ##
#################################################################

hadoop fs -put \
    ${INTERMEDIATE_DIR}/${MY_ASSOCIATIONS} \
    ${HADOOP_INTERMEDIATE_DIR}/${MY_ASSOCIATIONS}
pig ${PIG_OPTIONS} \
    -p sites=${HADOOP_INTERMEDIATE_DIR}/${MY_SITES} \
    -p companies=${HADOOP_INTERMEDIATE_DIR}/${MY_COMPANIES} \
    -p associations=${HADOOP_INTERMEDIATE_DIR}/${MY_ASSOCIATIONS} \
    -p sites_w_company=${HADOOP_INTERMEDIATE_DIR}/${MY_SITES_W_COMPANY} \
    -p sites_wo_company=${HADOOP_INTERMEDIATE_DIR}/${MY_SITES_WO_COMPANY} \
    ${PIG_SCRIPTS}/split_sites_w_and_wo_companies.pig

###################################################################
## Generating Restrictions                                       ##
##                                                               ##
## Dependencies:                                                 ##
##   + SITES_W_COMPANY                                           ##
## Produces:                                                     ##
##   + RESTICTIONS :: A Python Shelve with constraints to select ##
##     negative Samples                                          ##
##                                                               ##
###################################################################

hadoop fs -get \
    ${HADOOP_INTERMEDIATE_DIR}/${MY_SITES_W_COMPANY} \
    ${INTERMEDIATE_DIR}/${MY_SITES_W_COMPANY}
md_make_restrictions \
    ${INTERMEDIATE_DIR}/${MY_RESTRICTIONS} \
    ${INTERMEDIATE_DIR}/${MY_SITES_W_COMPANY}

#################################################################
## Generating the Tstamp to Seconds since Epoch file           ##
##                                                             ##
## Dependencies:                                               ##
##   + ALEXA_FILES                                             ##
## Produces:                                                   ##
##   + TSTAMP_TO_SECS :: A mapping from time-stamps to seconds ##
##     since Epoch                                             ##
##                                                             ##
#################################################################

md_tstamp_to_secs \
    ${INTERMEDIATE_DIR}/${MY_ALEXA_FILES} \
    > ${INTERMEDIATE_DIR}/${MY_TSTAMP_TO_SECS}

#################################################################
## Generate Negative Samples                                   ##
##                                                             ##
## Dependencies:                                               ##
##   + IDS_TO_SITES                                            ##
##   + RESTRICTIONS                                            ##
##   + SITES_WO_COMPANY                                        ##
##   + TSTAMP_TO_SECS                                          ##
##   Produces:                                                 ##
##   + SHAPED_NEGATIVE_SAMPLES :: Negative Samples in the form ##
##     id[TAB]secs_since_epoch                                 ##
##                                                             ##
#################################################################

## Splitting up the Data

hadoop fs -get \
    ${HADOOP_INTERMEDIATE_DIR}/${MY_SITES_WO_COMPANY} \
    ${INTERMEDIATE_DIR}/${MY_SITES_WO_COMPANY}
num_lines=$( cat ${INTERMEDIATE_DIR}/${MY_SITES_WO_COMPANY}/* | wc -l )
split_size=$(( ${num_lines} / ${NEGATIVE_TO_POSITIVE_SAMPLES_RATIO} + 1 ))
mkdir ${INTERMEDIATE_DIR}/${MY_SITES_WO_COMPANY_SPLITS}
cat ${INTERMEDIATE_DIR}/${MY_SITES_WO_COMPANY}/* \
    | split \
      -l ${split_size} \
      - \
      ${INTERMEDIATE_DIR}/${MY_SITES_WO_COMPANY_SPLITS}/split_

## Generate Negative Samples

mkdir ${INTERMEDIATE_DIR}/${MY_NEGATIVE_SAMPLES}
for f in ${INTERMEDIATE_DIR}/${MY_SITES_WO_COMPANY_SPLITS}/*; do
    out_f=${INTERMEDIATE_DIR}/${MY_NEGATIVE_SAMPLES}/$(basename ${f})
    shuf ${f} \
	| md_generate_negative_samples \
	  ${INTERMEDIATE_DIR}/${MY_RESTRICTIONS} \
	  > ${out_f}
done

## ## Shaping them
## 
## hadoop fs -put \
##     ${INTERMEDIATE_DIR}/${MY_NEGATIVE_SAMPLES} \
##     ${HADOOP_INTERMEDIATE_DIR}/${MY_NEGATIVE_SAMPLES}
## hadoop fs -put \
##     ${IDS_TO_SITES} \
##     ${HADOOP_INTERMEDIATE_DIR}/${MY_IDS_TO_SITES}
## hadoop fs -put \
##     ${INTERMEDIATE_DIR}/${MY_TSTAMP_TO_SECS} \
##     ${HADOOP_INTERMEDIATE_DIR}/${MY_TSTAMP_TO_SECS}
## pig ${PIG_OPTIONS} \
##     -p samples=${HADOOP_INTERMEDIATE_DIR}/${MY_NEGATIVE_SAMPLES} \
##     -p ids_to_sites=${HADOOP_INTERMEDIATE_DIR}/${MY_IDS_TO_SITES} \
##     -p tstamps_to_secs=${HADOOP_INTERMEDIATE_DIR}/${MY_TSTAMP_TO_SECS} \
##     -p output=${HADOOP_INTERMEDIATE_DIR}/${MY_SHAPED_NEGATIVE_SAMPLES} \
##     ${PIG_SCRIPTS}/prepare_samples.pig
## 
## ## Save them locally
## 
## hadoop fs -get \
##     ${HADOOP_INTERMEDIATE_DIR}/${MY_SHAPED_NEGATIVE_SAMPLES} \
##     ${INTERMEDIATE_DIR}/${MY_SHAPED_NEGATIVE_SAMPLES}
## 
## 
## #################################
## ## Generate Positive Samples   ##
## ##                             ##
## ## Dependencies:               ##
## ##   + IDS_TO_SITES            ##
## ##   + RESTRICTIONS            ##
## ##   + TSTAMP_TO_SECS          ##
## ## Produces:                   ##
## ##   + SHAPED_POSITIVE_SAMPLES ##
## ##                             ##
## #################################
## 
## md_generate_positive_samples \
##     ${INTERMEDIATE_DIR}/${MY_RESTRICTIONS} \
##     > ${INTERMEDIATE_DIR}/${MY_POSITIVE_SAMPLES}
## 
## ## Shaping them
## 
## hadoop fs -put \
##     ${INTERMEDIATE_DIR}/${MY_POSITIVE_SAMPLES} \
##     ${HADOOP_INTERMEDIATE_DIR}/${MY_POSITIVE_SAMPLES}
## pig ${PIG_OPTIONS} \
##     -p samples=${HADOOP_INTERMEDIATE_DIR}/${MY_POSITIVE_SAMPLES} \
##     -p ids_to_sites=${HADOOP_INTERMEDIATE_DIR}/${MY_IDS_TO_SITES} \
##     -p tstamps_to_secs=${HADOOP_INTERMEDIATE_DIR}/${MY_TSTAMP_TO_SECS} \
##     -p output=${HADOOP_INTERMEDIATE_DIR}/${MY_SHAPED_POSITIVE_SAMPLES} \
##     ${PIG_SCRIPTS}/prepare_samples.pig
## 
## ## Save them locally
## 
## hadoop fs -get \
##     ${HADOOP_INTERMEDIATE_DIR}/${MY_SHAPED_POSITIVE_SAMPLES} \
##     ${INTERMEDIATE_DIR}/${MY_SHAPED_POSITIVE_SAMPLES}
## 
## 
## ############
## ## Raport ##
## ############
## 
## echo "Negative Samples can be found in"
## echo "${INTERMEDIATE_DIR}/${MY_SHAPED_NEGATIVE_SAMPLES}"
## echo
## echo "Positve Samples can be found in"
## echo "${INTERMEDIATE_DIR}/${MY_SHAPED_POSITIVE_SAMPLES}"
