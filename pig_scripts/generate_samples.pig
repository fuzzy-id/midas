import 'macros.pig';

assocs = load_associations();
sites = load_sites();
cb = load_filtered_cb();

A = JOIN cb BY company, assocs BY company USING 'replicated';
B = JOIN sites BY site LEFT OUTER, 
  A BY assocs::site USING 'replicated';

sites_companies = FOREACH B GENERATE sites::site AS site,
		  	    	     sites::ranking AS ranking,
				     A::cb::company AS company,
				     A::cb::code AS code,
				     A::cb::tstamp AS tstamp;
