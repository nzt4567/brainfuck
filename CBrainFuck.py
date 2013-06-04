#!/usr/bin/env python

'''
  Brainfuck (http://en.wikipedia.org/wiki/Brainfuck) programming language
  interpreter published under GNU GPL v3.

  Author: nzt4567 (nzt4567 (at) gmx (dot) com)                 Year: 2013
'''

# IMPORTS
import os.path, sys, argparse

# CREDITS
__author__  = "nzt4567"
__email__   = "nzt4567@gmx.com"
__status__  = "Completed"
__version__ = "0.1"
__license__ = "GNU GPL v3"
__year__    = "2013"

############################ STANDARD HELPERS ###########################
def pa():
  ''' Parse arguments and return them '''
  
  p = argparse.ArgumentParser(description='''Brainfuck programming '''  +
  '''language interpreter. Requires Python 3.3''',
  epilog='''Created by: ''' + __author__ + '''; License: ''' + 
  __license__ + '''; Year: ''' + __year__ + '''; Please report ''' +
  '''bugs (bugs, what's that?) to ''' + __email__)

  # source
  p.add_argument('source', help='''path to program source file or ''' +
    '''the source code itself''')
  
  # -V / --version
  p.add_argument('-V', '--version', action='version',version='%(prog)s '+
                  __version__, help='''print program version and exit''')
  
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
  instruction_set = { '>': i_memInc,
                      '<': i_memDec,
                      '+': i_valInc,
                      '-': i_valDec,
                      '.': i_write,
                      ',': i_read,
                      '[': i_loopBeg,
                      ']': i_loopEnd }

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
      with open(data_) as f: # ... treat it's content as source code ...
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
  def __init__(self, data_, memory_=b'\x00', memory_pointer_=0):
    ''' Parse, execute and store output of code in data. '''

    try: # Process the input and convert it to dict()
      self.data = self.process_input(data_)
    except (OSError, IOError, TypeError, ValueError) as e:
      exit_failure("BF_PROCESS_INPUT", create_error_msg("PYTHON", e))

    try: # Execute the programme in self.data
      self.output, self.memory, self.memory_pointer = \
        self.execute_code(self.data, bytearray(memory_), memory_pointer_)
    except (OSError, TypeError, ValueError, IndexError) as e:
      exit_failure("BF_EXECUTE_CODE", create_error_msg("PYTHON", e))

    self.output = ''.join(self.output)

if __name__ == '__main__':
  a = pa()
  BrainFuck(a['source'])