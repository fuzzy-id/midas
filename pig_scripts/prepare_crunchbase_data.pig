cb_data = LOAD 'crunchbase';
DEFINE prepare `prepare_crunchbase.py` SHIP('prepare_crunchbase.py');
prepared = STREAM cb_data THROUGH prepare AS 
	 (id: chararray, hp: chararray, round: chararray, tstamp: chararray);
STORE prepared INTO 'prepared_crunchbase';