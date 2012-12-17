import 'macros.pig';

sites = load_sites();

DEFINE sample `generate_samples.py` SHIP('generate_samples.py', 
       	      			    	 'restrictions.py',
					 'restrictions_shelve');

samples = STREAM THROUGH sample AS 
	(site:chararray, company: chararray, tstamp: chararray);

grouped = GROUP samples BY company;

STORE grouped INTO 'grouped_samples';