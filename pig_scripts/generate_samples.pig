import 'macros.pig';

assocs = load_associations();
sites = load_sites();
cb = load_filtered_cb();

A = JOIN sites BY site LEFT OUTER, 
  assocs BY site USING 'replicated';
B = JOIN A BY assocs::company LEFT OUTER,
  cb BY company USING 'replicated';
