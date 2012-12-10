top1m = LOAD 'alexa_files' 
      USING JsonLoader('site:chararray,rank:int,tstamp:chararray');

sites = GROUP top1m BY site;
row = FOREACH sites {
    trend = FOREACH top1m GENERATE tstamp, rank;
    GENERATE group AS site, trend;
}

STORE row INTO 'trend.gz' USING JsonStorage();

site_count = FOREACH row GENERATE site, COUNT(trend) AS count;
STORE site_count INTO 'site_count.gz' USING JsonStorage();
