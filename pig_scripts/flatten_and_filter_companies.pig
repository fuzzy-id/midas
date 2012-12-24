DEFINE prepare `../pig_python_wrapper.sh prepare_crunchbase.py` 
       SHIP('../pig_python_wrapper.sh');

cb_data = LOAD '$input';

flattened = STREAM cb_data THROUGH prepare AS 
	  (id: chararray, hp: chararray, code: chararray, tstamp: chararray);

filtered = FILTER data BY hp is not null AND code is not null;

STORE filtered INTO '$output';
