top1m = LOAD 'alexa_files' 
      USING JsonLoader('site:chararray, rank:int, tstamp:chararray');

sites = GROUP top1m BY site;
row = FOREACH sites {
    ranking = FOREACH top1m GENERATE tstamp, rank;
    GENERATE group AS site, ranking;
}

STORE row INTO 'alexa_sites';
