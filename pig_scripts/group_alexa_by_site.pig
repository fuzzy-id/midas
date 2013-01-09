top1m = LOAD '$input' AS
      (site:chararray, tstamp:chararray, rank:int);

adult_sites = LOAD '$adult_sites' AS site: chararray;

wo_path = FILTER top1m BY (NOT site MATCHES '.+/.+');
joined = JOIN wo_path BY site LEFT OUTER, adult_sites BY site USING 'replicated';
not_adult_sites = FILTER joined BY adult_sites::site is null;

sites = GROUP not_adult_sites BY wo_path::site;
rows = FOREACH sites GENERATE group, not_adult_sites.(wo_path::tstamp, wo_path::rank);

STORE rows INTO '$output';
