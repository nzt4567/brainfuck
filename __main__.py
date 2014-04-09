#!/usr/bin/env python

''' bF/bL/bC interpreter; author: nzt4567; year: 2012/2013 '''

# IMPORTS
import std, brainx

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
    brainx.BrainFuck(a['source'])
  elif a['type'] == 'L':
    brainx.BrainLoller(a['source'])
  else:
    brainx.BrainCopter(a['source'])

if __name__ == '__main__':
    main()