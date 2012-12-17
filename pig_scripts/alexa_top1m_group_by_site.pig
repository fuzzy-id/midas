top1m = LOAD 'alexa_files' AS
      (site:chararray, rank:int, tstamp:chararray);

sites = GROUP top1m BY site;
row = foreach sites generate group, top1m.(tstamp, rank);

STORE row INTO 'alexa_sites';
