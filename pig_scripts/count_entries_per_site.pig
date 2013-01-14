sites = LOAD '$sites' AS 
      (site: chararray, ranking: bag{(tstamp: chararray, rank: int)});
site_count = FOREACH sites GENERATE site, COUNT(ranking) AS count;
STORE site_count INTO '$site_count';
