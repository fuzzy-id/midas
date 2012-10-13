.. _invert_index:

===========================================
 Invert the Index of the Alexa Top1M Files
===========================================

The data as provided by Alexa is rather unhandy for our purpose. We
therefor first invert the index of the data in a MapReduce job. Here
are the steps needed to do so::

   $ hadoop fs -put alexa-top-1m/ alexa-files
   $ cd alexa-top-1m
   $ ls top-1m-201*
   top-1m-2010-12-13.csv.zip
   top-1m-2010-12-20.csv.zip
   top-1m-2010-12-27.csv.zip
   […]
   $ for f in top-1m-201*; do echo "alexa-files/${f}"; done > ../infile
   $ hadoop fs -mkdir input
   $ cd ~/src/project-midas/trunk
   $ python setup.py develop
   $ cp run_alexa_to_key_to_files.sh.example \
      run_alexa_to_key_to_files.sh
   # Adapt `run_alexa_to_key_to_files.sh` to your needs
   $ ./run_alexa_to_key_to_files.sh

