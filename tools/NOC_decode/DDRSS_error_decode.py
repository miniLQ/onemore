#!/usr/bin/python

# ---------
# DDRSS_feac_error_decode.py
# ---------

import argparse, os, re
from collections import defaultdict

# Class for DDRSS FEAC error decoding

class DDRSS_FEAC_Decoding(object):
  def __init__(self,target,llcc,syndrome):
    try:
      exec("import data_%s as data" % target, globals())
    except Exception as e:
      print((str(e)))
      error = "\nThe target %s is not supported\nTargets supported: " % target
      files = [f for f in os.listdir('.') if os.path.isfile(f)]
      for f in files:
        if re.match("^data_(.+).py$", f):
          error += re.search("^data_(.+).py$", f).group(1) + ' '
      raise LookupError(error)

    # Retrieve LLCC settings.
    if 'ddrss_error_data' not in dir(data):
      error = "\nThe target %s is has no support for ddrss_error_data. " % target
      raise LookupError(error)

    self.syndrome = syndrome
    # {'interleave_num': 4, 'interleave_grain': 256}
    # FEAC :  {'feac': 'llcc0', 'regs': {'llcc': 'LLCC0', 'fe': 'FEAC', 'ERR_STATUS1': '7fc00000', 'ERR_STATUS2': '12f00', 'ERR_STATUS3': '21', 'ERR_STATUS4': 'c1', 'ERR_STATUS5': '1800', 'line_num': 93}}
    self.llcc = syndrome['llcc']
    address = int(syndrome['ERR_STATUS1'],16)
    inter_size = data.ddrss_error_data['interleave_grain']
    inter_num = data.ddrss_error_data['interleave_num']
    fill_bits = 3
    if 'feac_fill_bits' in data.ddrss_error_data:
      fill_bits = data.ddrss_error_data['feac_fill_bits']

    # ERR_STAT
    # Project: ERR_STATUS1;  ADDR_WIDTH; LLCC INTERLEAVING BITs
    # Lahaina:  35:10, 7:3;      35    ; [9,8]
    #           high,  low;               mid
    # To reconstruct, i.e. lahaina, the interleave_grain is 256, the interleave_num is 4.
    # low_addr = bottom 5 bits, which is masked with (interleave_grain/8-1) or 0x1F
    low_addr = (address & int((inter_size>>fill_bits)-1))
    # mid_addr = LLCC channel number which interleaves it
    mid_addr = int(re.match('llcc([0-9]+)', syndrome['llcc'], flags=re.IGNORECASE).group(1))
    # high_addr = addr - low_addr
    high_addr = address - low_addr
    # reconstruct inserting 3 LSBs of 0, put mid at the interleave bound,
    # and high is shifted by interleave size and number of interleaved channels.
    full_addr = (low_addr << fill_bits) + (mid_addr * inter_size) + ((high_addr * inter_num) << fill_bits)
    self.address = full_addr

    self.scid = (int(syndrome['ERR_STATUS2'],16) & 0xff)
    status4 = int(syndrome['ERR_STATUS4'],16)
    self.len_bytes = ((status4 >> 12) & 0x3f)  # len_bytes bits [17:12]
    self.awrite = ((status4 >> 1) & 0x1)       # awrite bit 1
    self.aburst = (status4 & 0x1)              # aburst bit 0

    status5 = int(syndrome['ERR_STATUS5'],16)
    self.amssselfauth = ((status5 >> 15) & 0x1) # MSA bit
    self.asecureproc =  ((status5 >> 14) & 0x1) # secproc
    self.aprotns =      ((status5 >> 13) & 0x1) # non-secure
    self.aewd =         ((status5 >>  6) & 0x1) # clean evict


  op_str = [['single read', 'burst read'], ['single write', 'burst write']]
  def __repr__(self):
    output = "*******************************\n"
    output += "DDRSS Front End Address Channel Error\n"
    output += "ERR_STATUS1 = %s\n" % self.syndrome['ERR_STATUS1']
    output += "ERR_STATUS2 = %s\n" % self.syndrome['ERR_STATUS2']
    output += "ERR_STATUS3 = %s\n" % self.syndrome['ERR_STATUS3']
    output += "ERR_STATUS4 = %s\n" % self.syndrome['ERR_STATUS4']
    output += "ERR_STATUS5 = %s\n" % self.syndrome['ERR_STATUS5']
    output += "\n"
    output += "FEAC %s\n" % self.llcc
    output += "%s\n" % DDRSS_FEAC_Decoding.op_str[self.awrite][self.aburst]
    # Needs fix, shows zero.  # output += 'length(bytes) = 0x%x\n' % self.len_bytes
    output += 'MSA %d, SECPROC %d, NonSec %d\n' % ( self.amssselfauth, self.asecureproc, self.aprotns )
    output += 'clean evict(aewd) = %d\n' % self.aewd
    output += 'SCID = 0x%x\n' % self.scid
    output += 'Address = 0x%x\n' % self.address

    return output


class DDRSS_FEWC_Decoding(object):
  def __init__(self,target,llcc,syndrome):
    try:
      exec("import data_%s as data" % target, globals())
    except Exception as e:
      print((str(e)))
      error = "\nThe target %s is not supported\nTargets supported: " % target
      files = [f for f in os.listdir('.') if os.path.isfile(f)]
      for f in files:
        if re.match("^data_(.+).py$", f):
          error += re.search("^data_(.+).py$", f).group(1) + ' '
      raise LookupError(error)

    # Retrieve LLCC settings.
    if 'ddrss_error_data' not in dir(data):
      error = "\nThe target %s is has no support for ddrss_error_data. " % target
      raise LookupError(error)

    self.syndrome = syndrome
    # {'interleave_num': 4, 'interleave_grain': 256}
    inter_size = data.ddrss_error_data['interleave_grain']
    inter_num = data.ddrss_error_data['interleave_num']
    fill_bits = 4
    if 'fewc_fill_bits' in data.ddrss_error_data:
      fill_bits = data.ddrss_error_data['fewc_fill_bits']

    self.llcc = syndrome['llcc']
    #FEWC :  {'fewc': 'llcc0', 'regs': {'llcc': 'LLCC0', 'fe': 'FEWC', 'ERR_STATUS1': '00000003', 'ERR_STATUS2': '00560000', 'ERR_STATUS3': '0000451e', 'ERR_STATUS4': '00000032',     'ERR_STATUS5': '00016818', 'line_num': 5}}
    address = int(syndrome['ERR_STATUS2'],16)
    low_addr = (address & int((inter_size>>fill_bits)-1))
    mid_addr = int(re.match('llcc([0-9]+)', syndrome['llcc'], flags=re.IGNORECASE).group(1))
    high_addr = address - low_addr
    full_addr = (low_addr << fill_bits) + (mid_addr * inter_size) + (high_addr * inter_num << fill_bits)
    # print([s for s in map(hex, (low_addr, mid_addr, high_addr, full_addr))])
    self.address = full_addr

    status1 = int(syndrome['ERR_STATUS1'],16)
    self.err_cnt = status1 >> 16
    self.err_no_alloc = (status1>>2) & 0x1
    self.err_partial_wr = (status1>>1) & 0x1

    status3 = int(syndrome['ERR_STATUS3'],16)
    self.scid = (status3 >> 4) & 0xFF
    self.rrid = (status3 & 0xF)

    status5 = int(syndrome['ERR_STATUS5'],16)
    self.alen = (status5 >> 20) & 0xF
    self.aewd = (status5 >> 17) & 0x1
    self.wb_occpd = (status5 >> 16) & 0x1

  def __repr__(self):
    output = "*******************************\n"
    output += "DDRSS Front End Write Channel (TCM) Error\n"
    output += "ERR_STATUS1 = %s\n" % self.syndrome['ERR_STATUS1']
    output += "ERR_STATUS2 = %s\n" % self.syndrome['ERR_STATUS2']
    output += "ERR_STATUS3 = %s\n" % self.syndrome['ERR_STATUS3']
    output += "ERR_STATUS4 = %s\n" % self.syndrome['ERR_STATUS4']
    output += "ERR_STATUS5 = %s\n" % self.syndrome['ERR_STATUS5']
    output += "\n"
    output += "FEWC %s\n" % self.llcc
    output += 'error count = %d\n' % self.err_cnt
    output += 'no_alloc    = %d\n' % self.err_no_alloc
    output += 'partial_wr  = %d\n' % self.err_partial_wr
    # Needs fix, value nonsense. # output += 'SCID        = 0x%x\n' % self.scid
    output += 'RRID        = 0x%x\n' % self.rrid
    output += 'Address     = 0x%x\n' % self.address

    return output
