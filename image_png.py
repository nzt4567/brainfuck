#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
  PNG pictures parser
  Author: Tomas Kvasnicka
'''

# IMPORTS
import zlib

# CREDITS
__author__  = "Tomas Kvasnicka"
__email__   = "kvasntom@fit.cvut.cz"
__status__  = "Development"
__version__ = "0.1"
__license__ = "GNU GPL v3"
__year__    = "2013"

######################### E - WRONG PNG HEADER ##########################
class PNGWrongHeaderError(Exception):
  ''' EXCEPTION: file does not have a png header '''
  pass

######################### E - MISSING IHDR ##############################
class PNGMissingIHDR(Exception):
  ''' EXCEPTION: file is missing mandatory IHDR chunk '''
  pass

######################### E - MISSING IDAT ##############################
class PNGMissingIDAT(Exception):
  ''' EXCEPTION: file is missing mandatory IDAT chunk '''
  pass

######################### E - MISSING IEND ##############################
class PNGMissingIEND(Exception):
  ''' EXCEPTION: file is missing mandatory IEND chunk '''
  pass

######################### E - CORRUPTED PNG #############################
class PNGErrorCRC32(Exception):
  ''' EXCEPTION: file is corrupted '''
  pass

####################### E - UNDEFINED STRUCTURE #########################
class PNGNotImplementedError(Exception):
  ''' EXCEPTION: file has a structure we cannot process '''
  pass



############################# PNG PARSER ################################ 
class PngReader():
  ''' Parse png file and return list of it's pixels '''

###### PREDICTOR - http://www.w3.org/TR/PNG/#9Filter-type-4-Paeth #######
  def paeth(self, a_, b_, c_):
    ''' Paeth pixel predictor '''

    p  = a_ + b_ - c_
    pa = abs(p - a_)
    pb = abs(p - b_)
    pc = abs(p - c_)

    if pa <= pb and pa <= pc:
      return a_
    elif pb <= pc:
      return b_
    else:
      return c_

######## NONE FILTER - http://www.w3.org/TR/PNG/#9Filter-types ##########
  def sf_0(self, L_, p_, w_):
    ''' Scanline filter 0 - None '''

    return L_ # same line - filter does nothing

######## SUB FILTER - http://www.w3.org/TR/PNG/#9Filter-types ###########
  def sf_1(self, L_, p_, w_):
    ''' Scanline filter 1 - Sub '''

    nl = [L_[0]]  # new line after applying filter

    for i in range(1, w_):
      nl.append(tuple(map(lambda x,y: (x+y)%256, L_[i], nl[i-1])))

    return nl # new line after applying filter

######### UP FILTER - http://www.w3.org/TR/PNG/#9Filter-types ###########
  def sf_2(self, L_, p_, w_):
    ''' Scanline filter 2 - Up '''

    return [tuple(map(lambda x,y: (x+y)%256, L_[i], p_[i])) \
      for i in range(0, w_)] # new line after applying filter

### AVERAGE FILTER - http://www.w3.org/TR/PNG/#9Filter-type-3-Average ###
  def sf_3(self, L_, p_, w_):
    ''' Scanline filter 3 - Average '''

    nl = [tuple(map(lambda x,y: (x+(y//2))%256, L_[0], p_[0]))]
    
    for i in range(1, w_):
      nl.append(tuple(map(lambda x,y,z: (x+((y+z)//2))%256, L_[i], \
        nl[i-1], p_[i])))

    return nl # new line after applying filter

######## PAETH - http://www.w3.org/TR/PNG/#9Filter-type-4-Paeth #########
  def sf_4(self, L_, p_, w_):
    ''' Scanline filter 4 - Paeth '''

    nl = [tuple(map(lambda x, w, y, z: (x+self.paeth(w, y, z))%256,\
      L_[0], (0, 0, 0), p_[0], (0, 0, 0)))]

    for i in range(1, w_):
      nl.append(tuple(map(lambda x, w, y,z: (x+self.paeth(w, y, z))%256,\
        L_[i], nl[i-1], p_[i], p_[i-1])))

    return nl # new line after applying filter

########### PNG FILTERS - http://www.w3.org/TR/PNG/#9Filters ############
  scanline_filters =  { # pointers to filter functions
                        0 : sf_0,
                        1 : sf_1,
                        2 : sf_2,
                        3 : sf_3,
                        4 : sf_4 
                      }

  def scanlines(self, d_, w_, h_):
    ''' Prepare png for scanlines filter application '''
 
    ret = list() # png in format [(filter_num, [picture_line]), ...]
    j = 0 # helper index for moving in old png format (d_)
    for i in range(0, h_):
      ret.append((d_[j], [(d_[x+1], d_[x+2], d_[x+3]) \
        for x in range(j, 3*w_ + j, 3)])) 
      j += 3 * w_ + 1

    return ret

############################### CHUNK PARSING ###########################
  def idhr(self, ihdr_):
    ''' Parse IHDR chunk '''

    if ihdr_[:4] != b'\x00\x00\x00\r': # length must be always 13
      raise PNGNotImplementedError('File is not a valid png')

    if ihdr_[4:8] != b'IHDR': # type must be always b'IHDR'
      raise PNGMissingIHDR('File is not png')

    w = int.from_bytes(ihdr_[8:12], 'big')  # picture width
    h = int.from_bytes(ihdr_[12:16], 'big') # picture height
    if ihdr_[16:17] != b'\x08': # bit depth
      raise PNGNotImplementedError('File is not a valid png')
    if ihdr_[17:18] != b'\x02': # color type
      raise PNGNotImplementedError('File is not a valid png')
    if ihdr_[18:19] != b'\x00': # compression method
      raise PNGNotImplementedError('File is not a valid png')
    if ihdr_[19:20] != b'\x00': # filter method
      raise PNGNotImplementedError('File is not a valid png')
    if ihdr_[20:21] != b'\x00': # interlace
      raise PNGNotImplementedError('File is not a valid png')

    if zlib.crc32(ihdr_[4:21]) != int.from_bytes(ihdr_[21:], 'big'):
      raise PNGErrorCRC32('File is corrupted')
    else:
      return w, h

  def parse_png(self, png_):
    ''' Parse picture and return it's data + width + height '''

    s = 25 # first byte after IHDR chunk
    d = list() # list of IDAT chunks
    w, h = self.idhr(png_[:s]) # width, height of png_

    while 1:
      l = int.from_bytes(png_[s:s + 4], 'big')
      s +=4 # start of chunk after reading is's length
      if png_[s:s + 4] == b'IEND': # crc32 is OK because we can ...
        break # recognize b'IEND' and there are no data

      c = png_[s + 4:s + 4 + l] # chunk content - data
      if zlib.crc32(png_[s:s + 4 + l]) != \
      int.from_bytes(png_[s + 4 + l:s + 8 + l], 'big'): # crc32 check
        raise PNGErrorCRC32('File is corrupted')

      if png_[s:s + 4] == b'IDAT':
        d.append(c) # if chunk contains data => store them
      s += l + 8

      if l == 0 and d == b'': # missing IEND chunk
        raise PNGMissingIEND('File is not a png')
    
    if len(d) == 0:
      raise PNGMissingIDAT('File is not a png')

    return b''.join(d), w, h

####################### CONSTRUCTOR == PARSE PNG ########################
  def __init__(self, filepath):
    ''' Parse png into pixels '''

    try:
      with open(filepath, 'rb') as f:
        c = f.read()
    except (TypeError, ValueError, IOError, OSError) as e:
      raise IOError(e)

    if c[:8] != b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': # PNG header
      raise PNGWrongHeaderError(str(filepath) + ' is not a png')

    data, width, height = self.parse_png(c[8:])
    data = self.scanlines(bytearray(zlib.decompress(data)), \
      width, height)

    self.rgb = [self.scanline_filters[data[0][0]](self, data[0][1],\
      [(0, 0, 0) for x in range(0, width)], width)]

    for i in range(1, height):
      self.rgb.append(self.scanline_filters[data[i][0]](self, \
        data[i][1], self.rgb[i-1], width))