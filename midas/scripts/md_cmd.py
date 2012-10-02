# -*- coding: utf-8 -*-

import os
import os.path

def which(program):
   def is_exe(fpath):
      return (not os.path.isdir(fpath) 
              and os.path.exists(fpath) 
              and os.access(fpath, os.F_OK | os.X_OK))
   if is_exe(program):
       return program
   for path in os.environ["PATH"].split(os.pathsep):
       exe_file = os.path.join(path, program)
       if is_exe(exe_file):
           return exe_file
   return None


