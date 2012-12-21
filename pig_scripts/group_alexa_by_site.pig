top1m = LOAD '$input' AS
      (site:chararray, tstamp:chararray, rank:int);

sites = GROUP top1m BY site;
rows = foreach sites generate group, top1m.(tstamp, rank);

STORE rows INTO '$output';
