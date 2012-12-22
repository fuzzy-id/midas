top1m = LOAD '$input' AS
      (site:chararray, tstamp:chararray, rank:int);

sites = GROUP top1m BY site;
rows = FOREACH sites GENERATE group, top1m.(tstamp, rank);

STORE rows INTO '$output';
