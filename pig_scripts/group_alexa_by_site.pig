top1m = LOAD '$input' AS
      (site:chararray, tstamp:chararray, rank:int);

adult_sites = LOAD '$adult_sites' AS site: chararray;

wo_path = FILTER top1m BY (NOT site MATCHES '.+/.+');

grouped = GROUP wo_path BY site;

joined = JOIN grouped BY group LEFT OUTER, adult_sites BY site USING 'replicated';
not_adult_sites = FILTER joined BY adult_sites::site is null;

rows = FOREACH not_adult_sites GENERATE grouped::group, grouped::wo_path.(tstamp, rank);

STORE rows INTO '$output';
