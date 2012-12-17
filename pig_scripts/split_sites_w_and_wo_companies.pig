import 'macros.pig';

assocs = load_associations();
sites = load_sites();
cb = load_filtered_cb();

A = JOIN cb BY company, assocs BY company USING 'replicated';
B = JOIN sites BY site LEFT OUTER, 
  A BY assocs::site USING 'replicated';

SPLIT B INTO in_crunchbase IF A::cb::company is not null, 
             not_in_crunchbase OTHERWISE;

sites_w_company = FOREACH in_crunchbase GENERATE sites::site AS site,
		    	                         sites::ranking AS ranking,
						 A::cb::company AS company,
						 A::cb::code AS code,
				     		 A::cb::tstamp AS tstamp;

STORE sites_w_company INTO 'sites_w_company';

remaining_sites = FOREACH not_in_crunchbase GENERATE sites::site AS site,
		                                     sites::ranking AS ranking;

STORE remaining_sites INTO 'sites_wo_company';
