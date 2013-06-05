#!/usr/bin/env python
'''
  Brainfuck / Brainloller / Braincopter programming language interpreter.

  Author: nzt4567 (nzt4567 (at) gmx (dot) com)                 Year: 2013
'''

# IMPORTS
import os.path, sys, argparse

# CREDITS
__author__  = "nzt4567"
__email__   = "nzt4567@gmx.com"
__status__  = "Development"
__version__ = "0.2"
__license__ = "GNU GPL v3"
__year__    = "2013"

############################ STANDARD HELPERS ###########################
def pa():
  ''' Parse arguments and return them '''
  
  p = argparse.ArgumentParser(description='''Brainfuck / Brainloller /''' 
    + ''' Braincopter programming language interpreter. Requires ''' +
    ''' Python 3.3''', epilog='''Created by: ''' + __author__ + '''; ''' 
    '''License: ''' + __license__ + '''; Year: ''' + __year__ + '''; '''
    '''Please report bugs (bugs, what's that?) to ''' + __email__)

  # source
  p.add_argument('source', help='''path to program source file or ''' +
    '''the source code itself''')
  
  # -V / --version
  p.add_argument('-V', '--version', action='version', version='%(prog)s '
    + __version__, help='''print program version and exit''')
  
  # -t / --type
  p.add_argument('-t', '--type', default='F', choices=['F', 'L', 'C'],
      help='''intepret program as brainFuck/brainLoller/brainCopter''')

  return vars(p.parse_args())

def exit_failure(code_, err_=None):
  ''' Exit with printing error message (if any) and correct exit code '''

  ec = { "INVALID_CODE": 1,
         "BF_PROCESS_INPUT": 10,
         "BF_EXECUTE_CODE": 15 }

  if code_ not in ec:
    code_ = "INVALID_CODE"

  if err_:
    print(err_)

  exit(ec[code_])

def create_error_msg(type_, value_, ignorable_=False):
  ''' Create and return error message in universal format '''

  err_types = { "WRONG_TYPE": "internal; wrong error type",
                "INTERNAL": "internal; general internal error",
                "PYTHON": "original python exception text",
                "EMPTY_SOURCE": "source file/string does not seem " +
                                "to contain instructions",
                "PARSING": "source code contains errors in loops" }

  if ignorable_ == True:
    err_level = "ignored error"
  else:
    err_level = "fatal error"

  if type_ not in err_types:
    type_ = "WRONG_TYPE"

  err_prog = os.path.split(sys.argv[0])[1]
  err_type = err_types[type_]
  err_value = value_
  
  return "[ERROR] {0}: {1}: {2}: \'{3}\'".format(err_prog, err_level, \
                                                 err_type, err_value)

################################# MAIN ##################################
if __name__ == '__main__':
  exit_failure("INVALID_CODE", "STD can only be imported, not run!")