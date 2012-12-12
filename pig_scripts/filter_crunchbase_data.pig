data = LOAD 'prepared_crunchbase' AS 
     (id: chararray, hp: chararray, code: chararray, tstamp:chararray);

filtered = FILTER data BY hp is not null AND code is not null;
STORE filtered INTO 'filtered_cb';
