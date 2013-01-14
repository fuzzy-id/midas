DEFINE flatten_cmd `$flatten_cmd`;
companies = LOAD '$crunchbase_companies';

flattened = STREAM companies THROUGH flatten_cmd AS 
	  (id: chararray, hp: chararray, code: chararray, tstamp: chararray);
filtered = FILTER flattened BY hp is not null AND code is not null;

STORE filtered INTO '$companies';
