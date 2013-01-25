samples = LOAD '$samples' 
	AS (site: chararray, tstamp: chararray, class: chararray);

ids_to_sites = LOAD '$ids_to_sites' AS (site_id: int, site: chararray);

tstamps_to_secs = LOAD '$tstamps_to_secs' AS (tstamp: chararray, sse: int);

indicators = LOAD '$indicators'
	   AS (site_id: int, 
	       B: bag{(sse: int, indicator: tuple(s: chararray))});

A = JOIN samples BY tstamp, 
         tstamps_to_secs BY tstamp 
	 USING 'replicated';
B = FOREACH A GENERATE samples::site AS site, 
                       tstamps_to_secs::sse AS sse, 
		       samples::class AS class;

C = JOIN ids_to_sites BY site, 
    	 B BY site
	 USING 'replicated';
D = FOREACH C GENERATE ids_to_sites::site_id AS site_id,
    	      	       B::site AS site,
    	      	       B::sse AS sse,
		       B::class AS class;

E = JOIN indicators BY site_id,
    	 D BY site_id
	 USING 'replicated';
F = FOREACH E GENERATE D::site AS site,
		       D::sse AS sse,
		       D::class AS class,
		       FLATTEN(indicators::B);

G = FILTER F BY indicators::B::sse <= sse;
H = GROUP G BY site;
I = FOREACH H {
    J = ORDER G BY B::sse DESC;
    K = LIMIT J 1;
    GENERATE K;
}

L = FOREACH I GENERATE FLATTEN(K);
features = FOREACH L GENERATE K::site AS site,
    	   	     	      K::class AS class,
			      FLATTEN(K::indicators::B::indicator);

STORE features INTO '$features' USING PigStorage(',');