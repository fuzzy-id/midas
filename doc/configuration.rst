.. _config:

===============
 Configuration
===============

All `midas` commands provide a ``--cfg`` option to alter the default
configuration. By default the file ``.midas`` residing in your home
directory is read when it is present. Although `midas` ships with
sensible default values there are way too much parameters. Thus you
most probably will not be able to get around this step. In order to
make it a bit easier `midas` ships the ``md_config`` command. If
called without any further arguments it simply prints the current
configuration.

`Midas` configuration file is read via Pythons :mod:`configparser`
module. You are encouraged to read the documentation provided for
everything that is beyond the scope of this documentation.


