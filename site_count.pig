TOP1M = LOAD 'alexa_files' 
      USING JsonLoader('site:chararray,rank:int,tstamp:chararray');
SITES = GROUP TOP1M BY site;
SITE_CNT = FOREACH SITES GENERATE group, COUNT(a);
STORE SITE_CNT INTO 'site_count.gz' USING JsonStorage();

SORT = ORDER TOP1M BY site, tstamp;
INVERTED = FOREACH SORT GENERATE site, tstamp, rank;
STORE INVERTED IN 'sites.gz';
