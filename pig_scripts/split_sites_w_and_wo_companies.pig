sites = LOAD '$sites' AS 
      (site: chararray, ranking: bag{(tstamp: chararray, rank: int)});
cb = LOAD '$companies' AS
   (company: chararray, hp: chararray, code: chararray, tstamp: chararray);
assocs = LOAD '$associations' AS
       (company: chararray, site: chararray);


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

sites_wo_company = FOREACH not_in_crunchbase GENERATE sites::site AS site,
		                                     sites::ranking AS ranking;

STORE sites_w_company INTO '$sites_w_company';
STORE sites_wo_company INTO '$sites_wo_company';
