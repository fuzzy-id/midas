
DEFINE sample_script `python_wrapper.sh generate_samples.py` 
       SHIP('python_wrapper.sh',
	    'generate_samples.py', 
	    'pig_schema.py',
            'restrictions.py',
	    'restrictions_shelve');

import 'macros.pig';

sites = load_sites();

samples = STREAM sites THROUGH sample_script AS 
	(site:chararray, company: chararray, tstamp: chararray);

grouped = GROUP samples BY company;

STORE grouped INTO 'grouped_samples';