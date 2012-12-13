DEFINE load_sites() RETURNS sites { 
       $sites = LOAD 'alexa_sites' AS 
       	    (site: chararray, ranking: bag{(tstamp: chararray, rank: int)});
};
