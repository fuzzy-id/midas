samples = LOAD '$samples' 
	AS (site: chararray, tstamp: chararray, class: chararray);

ids_to_sites = LOAD '$ids_to_sites' AS (site_id: int, site: chararray);

tstamps_to_sse = LOAD '$tstamps_to_sse' AS (tstamp: chararray, sse: int);

indicators = LOAD '$indicators'
	   AS (site_id: int, 
	       B: bag{(sse: int, indicator: tuple(v0: boolean, v1: boolean, v2: boolean))});

A = JOIN samples BY tstamp, 
         tstamps_to_sse BY tstamp 
	 USING 'replicated';
B = FOREACH A GENERATE samples::site AS site, 
                       tstamps_to_sse::sse AS sse, 
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
F = FOREACH E GENERATE D::site_id AS site_id,
    	      	       D::site AS site,
		       D::sse AS sse,
		       D::class AS class,
		       FLATTEN(indicators::B) as B;

G = FILTER F BY B::m <= sse;
H = GROUP G BY sse;
I = FOREACH H {
    J = ORDER G BY B::sse DESC;
    K = LIMIT J 1;
    GENERATE K;
}

L = FOREACH I GENERATE FLATTEN(K);
