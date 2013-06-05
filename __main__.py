#!/usr/bin/env python

''' bF/bL/bC interpreter; author: nzt4567; year: 2013 '''

# IMPORTS
import std, CBrainFuck

# CREDITS
__author__  = std.__author__
__email__   = std.__email__
__status__  = std.__status__
__version__ = std.__version__
__license__ = std.__license__
__year__    = std.__year__

################################# MAIN ##################################
def main():
  ''' Run the program '''

  a = std.pa()
  if a['type'] == 'F':
    CBrainFuck.BrainFuck(a['source'])
  elif a['type'] == 'L':
  	pass
  else:
  	pass

if __name__ == '__main__':
    main()