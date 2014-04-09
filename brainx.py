#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' 
  BrainFuck/BrainLoller/BrainCopter programming language interpreters
  Author: nzt4567; Mail: nzt4567@gmx.com; Year: 2012/2013
'''

# IMPORTS
import std, os.path, sys, image_png

# CREDITS
__author__  = std.__author__
__email__   = std.__email__
__status__  = std.__status__
__version__ = std.__version__
__license__ = std.__license__
__year__    = std.__year__


############################ BF INTERPRETER #############################
class BrainFuck():
  ''' BrainFuck programming language interpreter '''
 
############################ INSTRUCTIONS ###############################
  def i_memInc(self, mem_, p_mem_, code_, ip_, out_):
    ''' Execute > instruction '''
    
    p_mem_ += code_[ip_][1]
    if len(mem_) <= p_mem_:
      mem_ += b'\x00' * code_[ip_][1]

    return ip_ + code_[ip_][1], p_mem_

  def i_memDec(self, mem_, p_mem_, code_, ip_, out_):
    ''' Execute < instruction '''
    
    p_mem_ -= code_[ip_][1]
    if p_mem_ < 0:
      p_mem_ = 0

    return ip_ + code_[ip_][1], p_mem_

  def i_valInc(self, mem_, p_mem_, code_, ip_, out_):
    ''' Execute + instruction '''
    
    mem_[p_mem_] = (mem_[p_mem_] + code_[ip_][1]) % 256
    return ip_ + code_[ip_][1], p_mem_

  def i_valDec(self, mem_, p_mem_, code_, ip_, out_):
    ''' Execute - instruction '''

    mem_[p_mem_] = (mem_[p_mem_] - code_[ip_][1]) % 256
    return ip_ + code_[ip_][1], p_mem_

  def i_write(self, mem_, p_mem_, code_, ip_, out_):
    ''' Execute . instruction '''
    
    out_.append(chr(mem_[p_mem_]) * code_[ip_][1])
    sys.stdout.write(chr(mem_[p_mem_]) * code_[ip_][1])
    sys.stdout.flush()
    return ip_ + code_[ip_][1], p_mem_

  def i_read(self, mem_, p_mem_, code_, ip_, out_):
    ''' Execute , instruction '''
    
    if 'stdin' in code_:
      i = 0
      while len(code_['stdin']) >= 1 and i < code_[ip_][1]:
        i += 1
        mem_[p_mem_] = ord(code_['stdin'][0]) % 256
        code_['stdin'] = code_['stdin'][1:]
    else:
      for x in range(0, code_[ip_][1]):
        mem_[p_mem_] = ord(sys.stdin.read(1)) % 256

    return ip_ + code_[ip_][1], p_mem_

  def i_loopBeg(self, mem_, p_mem_, code_, ip_, out_):
    ''' Execute [ instruction '''
    
    if mem_[p_mem_] == 0:
      return code_[ip_][1], p_mem_

    return ip_ + 1, p_mem_

  def i_loopEnd(self, mem_, p_mem_, code_, ip_, out_):
    ''' Execute ] instruction '''
    
    if mem_[p_mem_] != 0:
      return code_[ip_][1], p_mem_

    return ip_ + 1, p_mem_ 

############################# INSTRUCTION SET ###########################
  instruction_set = { 
                      '>': i_memInc,
                      '<': i_memDec,
                      '+': i_valInc,
                      '-': i_valDec,
                      '.': i_write,
                      ',': i_read,
                      '[': i_loopBeg,
                      ']': i_loopEnd 
                    }

######################### PARSER && INTERPRETER #########################
  def bf2dict(self, data_):
    ''' Convert source code into internal form for faster execution '''

    def save_prev():
      ''' Save previous instruction into dict() '''

      nonlocal prev, c
      if prev[0] in nc:
        p[prev[1]] = (prev[0], c)
      prev = (data_[i], i)
      c = 1

    p = dict() # Program in internal form
    s = list() # Stack for loops parsing
    L = len(data_) # Input length
    i = 0 # Helper IP
    c = 0 # Same instructions counter
    prev = (data_[i], i) # Previous inst. (instr_type, instr_addr)
    nc = ('>', '<', '+', '-', '.', ',') # Non-control instructions

    for i in range(0, L): # Convert source code to dict() representation
      if data_[i] in nc:
        if data_[i] == prev[0]:
          c += 1
        else:
          save_prev()
      elif data_[i] == '[':
        save_prev()
        s.append(i)
      elif data_[i] == ']':
        save_prev()
        a = s.pop()
        p[a] = ('[', i + 1)
        p[i] = (']', a)
      elif data_[i] == '!':
        p['stdin'] = data_[i + 1:]
        i -= 1
        break

    if prev[0] in nc:
      p[prev[1]] = (prev[0], c)
    p[i+1] = ('@', 0) # Add STOP instruction
    
    return p

  def process_input(self, data_):
    ''' Clean comments && separate input marked by ! from source code '''

    if os.path.isfile(data_): # If data_ is a file, ...
      with open(data_, encoding='ascii') as f: # ... it's source code ...
        data_ = f.read() # ... else data_ itself is treated as source 

    if '!' in data_: # Strip the input if there is any
      i = data_[data_.find('!'):]
      data_ = data_[:data_.find('!')]
    else:
      i = str()

    allowed_chars = list(self.instruction_set)
    for c in str(data_): # Get rid of comments
      if c not in allowed_chars:
        allowed_chars.append(c)
        data_ = data_.replace(c, '')

    if len(data_) == 0:
      raise ValueError("source code seems to be empty")

    return self.bf2dict(data_ + i)

  def execute_code(self, code_, mem_, p_mem_):
    ''' Run code in internal form '''

    ip = 0 # instruction pointer
    output = list() # stdout

    while code_[ip] != ('@', 0): # Execution stops at STOP instruction
      ip, p_mem_ = self.instruction_set[code_[ip][0]](self, mem_, p_mem_,\
                                                      code_, ip, output)

    return output, mem_, p_mem_

####################### CONSTRUCTOR == RUN PROGRAM ######################
  def __init__(self, data, memory=b'\x00', memory_pointer=0):
    ''' Parse, execute and store output of code in data '''

    try: # Process the input and convert it to dict()
      self.data = self.process_input(data)
    except (OSError, IOError, TypeError, ValueError, IndexError) as e:
      std.exit_failure("BF_PROCESS_INPUT", \
        std.create_error_msg("PYTHON", e))

    try: # Execute the programme in self.data
      self.output, self.memory, self.memory_pointer = \
        self.execute_code(self.data, bytearray(memory), memory_pointer)
    except (OSError, TypeError, ValueError, IndexError, KeyError) as e:
      std.exit_failure("BF_EXECUTE_CODE", std.create_error_msg("PYTHON", e))

    self.output = ''.join(self.output)

  def get_memory(self):
    return self.memory



############################ BL INTERPRETER #############################
class BrainLoller():
  ''' BrainLoller programming language interpreter '''

############################# CONVERT CODE TO BF ########################
  def process_input(self, png_):
    ''' Convert decoded PNG to BrainFuck program '''

    x = 0 # x coordinate (zero means left)
    y = 0 # y coordinate (zero means up)
    d = 0 # default exectuion direction (right)
    h = len(png_) # height
    w = len(png_[0]) # width
    code = list() # brainfuck code
    directions =  { # all possible directions to move in code
                    0: lambda x, y: (x+1, y), # go R
                    1: lambda x, y: (x, y+1), # go D
                    2: lambda x, y: (x-1, y), # go L
                    3: lambda x, y: (x, y-1)  # go U
                  }
    instruction_set = { # instructions convertable to BF instructions
                        (255, 0, 0): '>',
                        (128, 0, 0): '<',
                        (0, 255, 0): '+',
                        (0, 128, 0): '-',
                        (0, 0, 255): '.',
                        (0, 0, 128): ',',
                        (255, 255, 0): '[',
                        (128, 128, 0): ']'
                      }
    direction_change =  { # instructions changing IP direction
                          (0, 255, 255): lambda x: (x+1)%4, # rotate R
                          (0, 128, 128): lambda x: (x-1)%4  # rotate L 
                        }
    
    while 0 <= y < h and 0 <= x < w:
      if png_[y][x] in instruction_set:
        code.append(instruction_set[png_[y][x]])

      if png_[y][x] in direction_change:
        d = direction_change[png_[y][x]](d)

      x, y = directions[d](x, y)
    
    return ''.join(code)

####################### CONSTRUCTOR == RUN PROGRAM ######################
  def __init__(self, filename):
    ''' Decode, parse and execute program in PNG format '''

    try: # try to decode the png
      self.png = image_png.PngReader(filename)
    except (IOError, image_png.PNGErrorCRC32, image_png.PNGMissingIDAT,\
      image_png.PNGMissingIEND, image_png.PNGMissingIHDR) as e:
      std.exit_failure("BL_DECODE_PNG", \
        std.create_error_msg("PYTHON", e))

    try: # and try to create a brainfuck program from it
      self.data = self.process_input(self.png.rgb)
    except (TypeError, ValueError, KeyError, IndexError) as e:
      std.exit_failure("BL_PROCESS_INPUT", \
        std.create_error_msg("INTERNAL", e))

    self.program = BrainFuck(self.data)



############################ BC INTERPRETER #############################
class BrainCopter():
  ''' BrainCopter programming language interpreter '''

############################# CONVERT CODE TO BF ########################
  def process_input(self, png_):
    ''' Convert decoded PNG to BrainFuck program '''
    
    x = 0 # x coordinate (zero means left)
    y = 0 # y coordinate (zero means up)
    d = 0 # default exectuion direction (right)
    h = len(png_) # height
    w = len(png_[0]) # width
    code = list() # brainfuck code
    directions =  { # all possible directions to move in code
                    0: lambda x, y: (x+1, y), # go right
                    1: lambda x, y: (x, y+1), # go down
                    2: lambda x, y: (x-1, y), # go left
                    3: lambda x, y: (x, y-1)  # go up
                  }
    instruction_set = { # instructions convertable to BF instructions
                        0: '>',
                        1: '<',
                        2: '+',
                        3: '-',
                        4: '.',
                        5: ',',
                        6: '[',
                        7: ']' 
                      }
    direction_change =  { # instructions changing IP direction
                          8: lambda x: (x+1)%4, # rotate right 
                          9: lambda x: (x-1)%4  # rotate left 
                        }
    
    while 0 <= y < h and 0 <= x < w:
      i = (-2 * png_[y][x][0] + 3 * png_[y][x][1] + png_[y][x][2])%11
      if i in instruction_set:
        code.append(instruction_set[i])

      if i in direction_change:
        d = direction_change[i](d)

      x, y = directions[d](x, y)
      
    return ''.join(code)

####################### CONSTRUCTOR == RUN PROGRAM ######################
  def __init__(self, filename):
    ''' Decode, parse and execute program in PNG format '''
    
    try: # try to decode the png
      self.png = image_png.PngReader(filename)
    except (IOError, image_png.PNGErrorCRC32, image_png.PNGMissingIDAT,\
      image_png.PNGMissingIEND, image_png.PNGMissingIHDR) as e:
      std.exit_failure("BC_DECODE_PNG", \
        std.create_error_msg("PYTHON", e))

    try: # and try to create a brainfuck program from it
      self.data = self.process_input(self.png.rgb)
    except (TypeError, ValueError, KeyError, IndexError) as e:
      std.exit_failure("BC_PROCESS_INPUT", \
        std.create_error_msg("INTERNAL", e))

    self.program = BrainFuck(self.data)