top1m = LOAD '$alexa_files' AS
      (site:chararray, tstamp:chararray, rank:int);

adult_sites = LOAD '$adult_sites' AS site: chararray;

wo_path = FILTER top1m BY (NOT site MATCHES '.+/.+');

grouped = GROUP wo_path BY site;

minimized = FOREACH grouped GENERATE group AS site, wo_path.(tstamp, rank) AS ranking;

joined = JOIN minimized BY site LEFT OUTER, adult_sites BY site USING 'replicated';
not_adult_sites = FILTER joined BY adult_sites::site is null;

rows = FOREACH not_adult_sites GENERATE minimized::site as site, 
                                        minimized::ranking as ranking;

STORE rows INTO '$sites';
