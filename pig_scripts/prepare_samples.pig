
samples = LOAD '$samples' AS (site: chararray, tstamp: chararray);
id2site = LOAD '$ids_to_sites' AS (id: int, site: chararray);
tstamp2secs = LOAD '$tstamps_to_secs' AS (tstamp: chararray, secs: int);

A = JOIN samples BY tstamp, tstamp2secs BY tstamp USING 'replicated';
B = FOREACH A GENERATE samples::site AS site, tstamp2secs::secs AS secs;
C = JOIN id2site BY site, B BY site USING 'replicated';
D = FOREACH C GENERATE id2site::id AS id, B::secs AS secs;

STORE D into '$output';