-- Streams all Companies found in `$input' through flatten_companies.py.
-- `$input' is supposed to be the CrunchBase data in JSON format.

DEFINE prepare `../pig_python_wrapper.sh flatten_companies.py` 
       SHIP('../pig_python_wrapper.sh');

companies = LOAD '$input';

flattened = STREAM companies THROUGH prepare AS 
	  (id: chararray, hp: chararray, code: chararray, tstamp: chararray);

filtered = FILTER flattened BY hp is not null AND code is not null;

STORE filtered INTO '$output';
