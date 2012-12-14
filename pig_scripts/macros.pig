DEFINE load_sites() RETURNS sites { 
       $sites = LOAD 'alexa_sites' AS 
       	    (site: chararray, ranking: bag{(tstamp: chararray, rank: int)});
};

DEFINE load_filtered_cb() RETURNS cb {
       $cb = LOAD 'filtered_cb' AS
       	   (company: chararray, hp: chararray, code: chararray, tstamp: chararray);
};

DEFINE load_associations() RETURNS assocs {
       $assocs = LOAD 'associations' AS
       	       (company: chararray, site: chararray);
};
