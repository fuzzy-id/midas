TOP1M = LOAD 'alexa_files' 
      USING JsonLoader('site:chararray,rank:int,tstamp:chararray');

SORT = ORDER TOP1M BY site, tstamp;
INVERTED = FOREACH SORT GENERATE site, tstamp, rank;
STORE INVERTED INTO 'sites.gz';

SITES = GROUP TOP1M BY site;
SITE_CNT = FOREACH SITES GENERATE group, COUNT(TOP1M);
STORE SITE_CNT INTO 'site_count.gz';
