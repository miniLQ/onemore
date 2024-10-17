#!/usr/bin/python

# ---------
# NoC_error_decode.py
# ---------

import argparse, os, re
from collections import defaultdict
from functools import reduce

# Class for NoC error decoding exceptions

class DecodingError(Exception):
    pass

# Class for NoC error decoding

class NocDecoding(object):
  def __init__(self,target,noc,syndrome):
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

    # saving ERRLOG values
    self.obs         = syndrome['obs']
    self.sbm         = syndrome['sbm']

    # getting data for this target/noc
    self.data = data.data
    self.masters = data.masters
    if noc in self.data:
      self.noc_data = self.data[noc]
    else:
      error = "\nThe NoC " + noc + " is not supported\nNoCs supported: "
      error += ', '.join(list(self.data.keys()))
      raise DecodingError(error)

    # Do the decoding
    self.decode_faults()
    self.errcodes()
    self.path()
    self.extid()
    self.address_decode()
    self.decode_timeouts()

  def __repr__(self):
    output = ''
    if self.main_fault:
      output += '\nopcode = 0x%x = %s\n' % (self.opcode, self.opcode_str)
      output += 'errcode = 0x%x = %s\n' % (self.errcode, self.errcode_str)
      if self.to:
        output += 'time-out detected\n'
      if not self.loginfovld:
        output += '\npath = 0x%x\n' % (self.path_id)
        output += 'partial loginfo\n'
      else:
        output += '\npath = 0x%x\naddrspace = 0x%x\n' % (self.path_id, self.addrspace)
      output += '%s access\n' % self.security_str
      output += 'initiator = %s\n' % self.initiator
      output += 'target = %s\n' % self.target
      if self.loginfovld:
        output += 'BID = 0x%x\n' % self.bid
        output += 'PID = 0x%x\n' % self.pid
        output += 'MID = 0x%x\n' % self.mid
        output += 'BID/PID/MID = %s\n\n' % self.bpm_str
        output += 'Address offset = 0x%x\n' % self.address_offset
        output += 'Address base = 0x%x\n' % self.address_base
        output += 'Address = 0x%x\n' % self.address
        output += self.redirect_str
    output += self.to_str
    output += self.fault_str
    return output

  # decode the opcode/errcode/flag values
  def errcodes(self):
    self.errcodes    = self.noc_data['errcodes']
    self.errcode     = (self.obs['ERRLOG0_LOW'] >> 8) & 0x7
    self.errcode_str = self.errcodes.get(self.errcode, 'unknown')

    self.opcodes     = self.noc_data['opcodes']
    self.opcode      = (self.obs['ERRLOG0_LOW'] >> 4) & 0x7
    self.opcode_str  = self.opcodes.get(self.opcode, 'unknown')

    self.nonsecure   = (self.obs['ERRLOG0_LOW'] & 0x4) != 0
    if self.nonsecure:
      self.security_str = 'non-secure'
    else:
      self.security_str = 'secure'

    self.loginfovld = (self.obs['ERRLOG0_LOW'] & 0x1) != 0

  # decode the path
  def path(self):
    self.paths     = self.noc_data['paths']
    self.addrspace = (self.obs['ERRLOG0_LOW'] >> 16) & 0x3F
    self.path_id   = self.obs['ERRLOG1_LOW'] & 0xFFFF
    self.path      = self.paths.get((self.path_id, self.addrspace), {})
    self.initiator = self.path.get('initiator', 'invalid')
    self.target    = self.path.get('target', 'invalid')

  def extid(self):
    self.extid   = self.obs['ERRLOG1_HIGH'] & 0x3FFFF
    self.bid     = (self.extid >> 13) & 0x7
    self.pid     = (self.extid >> 8) & 0x1F
    self.mid     = self.extid & 0xFF
    self.bpm_str = self.masters.get((self.bid,self.pid,self.mid),self.masters.get((self.bid,self.pid), 'unknown'))

  # determine the address trying to be accessed
  def address_decode(self):
    self.redirect_str = ''
    self.address_offset = self.obs['ERRLOG2_LOW'] | (self.obs['ERRLOG2_HIGH'] << 32)
    self.outer_cacheable    = 0 != (self.address_offset & (1 << 36))
    if self.outer_cacheable:
      self.redirect_str += 'Outer cacheable flag set\n'
    self.io_coherent   = 0 != (self.address_offset & (1 << 37))
    if self.io_coherent:
      self.redirect_str += 'I/O coherent flag set\n'
    self.address_base   = self.path.get('addr_base','0')
    self.address_offset = self.address_offset & ~(3<<36)
    if self.address_base != 'NA':
      # Get the address base, but knock out any io coherency hint bits
      self.address_base = int(self.address_base, 16) & ~(3<<36)
      self.address      = self.address_base + self.address_offset
    else:
      self.target       = None
      self.address_base = 0x0
      self.address      = self.address_offset

  # decode any fault status bits
  def decode_faults(self):
    sbm_keys = ['FAULTINSTATUS0_LOW', 'FAULTINSTATUS0_HIGH', 'FAULTINSTATUS1_LOW', 'FAULTINSTATUS1_HIGH']

    self.faults = self.noc_data['faults']
    self.pos = self.noc_data.get('pos',{})
    self.pocs = self.noc_data.get('pocs',{})
    self.fault_str = ''
    faults = 0
    for i in sorted(self.sbm.keys()):
      shift = i * 128
      for key in sbm_keys:
        faults |= self.sbm[i][key] << shift
        shift += 32

    found = False
    # Full zero obs means nothing was actually logged.
    if reduce(lambda x,y: x+y, list(self.obs.values())) == 0:
      self.main_fault = False
    elif (('obs' in self.noc_data) and
        ((self.noc_data['obs']['obs_bit_pos'] is None) or (faults & (1<<self.noc_data['obs']['obs_bit_pos'])))):
      self.main_fault = True
    elif (('obs' not in self.noc_data) and (faults & 1)):
      self.main_fault = True
    else:
      self.main_fault = False
    if faults != 0 and len(self.faults) > 0:
      for i in range(128 * (max(self.sbm.keys())+1)):
        if ((1 << i) & faults) != 0 and i in self.faults:
          found = True
          self.fault_str += 'Unclocked access to %s.\n' % self.faults[i]['niu']
          self.fault_str += 'Potential targets:\n'
          for target in self.faults[i]['targets']:
            self.fault_str += '  %s\n' % target
          self.fault_str += '\n'
      if found:
        self.fault_str = '\nODSC faults detected:\n' + self.fault_str
    if faults != 0 and len(self.pos) > 0:
      for i in range(128 * (max(self.sbm.keys())+1)):
        if ((1 << i) & faults) != 0 and i in self.pos:
          found = True
          self.fault_str += '  %s\n' % self.pos[i]
      if found:
        self.fault_str = '\nPoS faults detected:\n' + self.fault_str
    if faults != 0 and len(self.pocs) > 0:
      for i in range(128 * (max(self.sbm.keys())+1)):
        if ((1 << i) & faults) != 0 and i in self.pocs:
          found = True
          self.fault_str += '  %s\n' % self.pocs[i]['niu']
      if found:
        self.fault_str = '\nPoC faults detected:\n' + self.fault_str

  # decode any time-out bits
  def decode_timeouts(self):
    sbm_keys = ['FAULTINSTATUS0_LOW', 'FAULTINSTATUS0_HIGH', 'FAULTINSTATUS1_LOW', 'FAULTINSTATUS1_HIGH']

    self.tos = self.noc_data.get('tos',{})
    faults = 0
    for i in sorted(self.sbm.keys()):
      shift = i * 128
      for key in sbm_keys:
        faults |= self.sbm[i][key] << shift
        shift += 32

    self.to = False
    self.to_str = ''
    if faults != 0 and len(self.tos) > 0:
      for i in range(128 * (max(self.sbm.keys())+1)):
        if ((1 << i) & faults) != 0 and i in self.tos:
          self.to = True
          self.to_str += '  %s\n' % self.tos[i]
    if self.to:
      self.to_str = '\nTime-out faults:\n' + self.to_str

class PocDecoding(object):
  def __init__(self,target,noc,index,syndrome):
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

    # getting data for this target/noc
    self.data = data.data
    self.masters = data.masters
    if noc in self.data:
      self.noc_data = self.data[noc]
    else:
      error = "\nThe NoC " + noc + " is not supported\nNoCs supported: "
      error += ', '.join(list(self.data.keys()))
      raise DecodingError(error)

    # Save syndrome
    self.syndrome = syndrome
    self.index = index

    # Do the decoding
    self.decode()

  def __repr__(self):
    output = '\npoc = %s\n' % (self.name)
    output += 'BID = 0x%x\n' % self.bid
    output += 'PID = 0x%x\n' % self.pid
    output += 'MID = 0x%x\n' % self.mid
    output += 'BID/PID/MID = %s\n' % self.bpm_str
    output += '%s\n\n' % self.nonsecure_str
    output += 'errcode = 0x%x (%s)\n' % (self.code, self.code_str)
    output += 'opcode  = 0x%x (%s)\n' % (self.opc, self.opc_str)
    output += 'socket  = 0x%x (%s)\n' % (self.socket, self.socket_str)
    output += 'channel = 0x%x (%s)\n' % (self.channel, self.channel_str)
    output += 'trtype  = 0x%x (%s)\n' % (self.trtype, self.trtype_str)
    output += 'length  = %d\n\n' % self.length
    output += 'Address = 0x%x\n' % self.addr
    return output

  def decode(self):
    # Try and get our PoC name
    pocs = self.noc_data.get('pocs', {})
    self.name = 'unknown'
    for poc in list(pocs.values()):
      if poc['index'] == self.index:
        self.name = poc['niu']

    # Decode fields
    self.decode_extid()
    self.decode_channel()
    self.decode_socket()
    self.decode_trtype()
    self.decode_opcode()
    self.decode_address()
    self.decode_errcode()
    self.decode_misc()

  def decode_extid(self):
    self.extid = self.syndrome['ERRLOGMAIN_LOW'] >> 8
    self.bid     = (self.extid >> 13) & 0x7
    self.pid     = (self.extid >> 8) & 0x1F
    self.mid     = self.extid & 0xFF
    self.bpm_str = self.masters.get((self.bid,self.pid,self.mid),self.masters.get((self.bid,self.pid), 'unknown'))

  def decode_channel(self):
    channel_dict = {
      0: 'QCI Req',
      1: 'QCI SRsp',
      2: 'QCI WDat',
      3: 'QCI WDatS',
      4: 'NTTP Rx',
      5: 'NTTP Rsp',
      7: 'Exclusive monitors',
    }
    self.channel = (self.syndrome['ERRLOGMAIN_LOW'] >> 1) & 0x7
    self.channel_str = channel_dict.get(self.channel, 'invalid')

  def decode_socket(self):
    socket_dict = {
      0: 'QCI datapath',
      1: 'NTTP datapath'
    }
    self.socket = self.syndrome['ERRLOGMAIN_LOW'] & 0x1
    self.socket_str = socket_dict.get(self.socket, 'invalid')

  def decode_trtype(self):
    trtype_dict = {
      0: 'DEV_NE',
      1: 'DEV_E',
      2: 'NORMAL',
      3: 'CACHED',
      4: 'SHARED',
      5: 'POSTED',
    }
    self.trtype = (self.syndrome['ERRLOGMAIN_HIGH'] >> 16) & 0x7
    self.trtype_str = trtype_dict.get(self.trtype, 'reserved')

  def decode_opcode(self):
    opc_nttp_dict = self.noc_data.get('opcodes', {})
    opc_chi_req_dict = {
      0x00: 'ReqLCrdReturn',
      0x01: 'ReadShared',
      0x02: 'ReadClean',
      0x03: 'ReadOnce',
      0x04: 'ReadNoSnp',
      0x05: 'PCrdReturn',
      0x07: 'ReadUnique',
      0x08: 'CleanShared',
      0x09: 'CleanInvalid',
      0x0A: 'MakeInvalid',
      0x0B: 'CleanUnique',
      0x0C: 'MakeUnique',
      0x0D: 'Evict Reserved',
      0x0E: 'Reserved (EOBarrier)',
      0x0F: 'Reserved (ECBarrier)',
      0x11: 'ReadNoSnpSep',
      0x13: 'CleanSharedPersistSep',
      0x14: 'DVMOp',
      0x15: 'WriteEvictFull',
      0x16: 'Reserved (WriteCleanPtl)',
      0x17: 'WriteCleanFull',
      0x18: 'WriteUniquePtl',
      0x19: 'WriteUniqueFull',
      0x1A: 'WriteBackPtl',
      0x1B: 'WriteBackFull',
      0x1C: 'WriteNoSnpPtl',
      0x1D: 'WriteNoSnpFull',
      0x20: 'WriteUniqueFullStash',
      0x21: 'WriteUniquePtlStash',
      0x22: 'StashOnceShared',
      0x23: 'StashOnceUnique',
      0x24: 'ReadOnceCleanInvalid',
      0x25: 'ReadOnceMakeInvalid',
      0x26: 'ReadNotSharedDirty',
      0x27: 'CleanSharedPersist',
      0x28: 'AtomicStore.ADD',
      0x29: 'AtomicStore.CLR',
      0x2A: 'AtomicStore.EOR',
      0x2B: 'AtomicStore.SET',
      0x2C: 'AtomicStore.SMAX',
      0x2D: 'AtomicStore.SMIN',
      0x2E: 'AtomicStore.UMAX',
      0x2F: 'AtomicStore.UMIN',
      0x30: 'AtomicLoad.ADD',
      0x31: 'AtomicLoad.CLR',
      0x32: 'AtomicLoad.EOR',
      0x33: 'AtomicLoad.SET',
      0x34: 'AtomicLoad.SMAX',
      0x35: 'AtomicLoad.SMIN',
      0x36: 'AtomicLoad.UMAX',
      0x37: 'AtomicLoad.UMIN',
      0x38: 'AtomicSwap',
      0x39: 'AtomicCompare',
      0x3A: 'PrefetchTgt',
      0x41: 'MakeReadUnique',
      0x42: 'WriteEvictOrEvict',
      0x43: 'WriteUniqueZero',
      0x44: 'WriteNoSnpZero',
      0x47: 'StashOnceSepShared',
      0x48: 'StashOnceSepUnique',
      0x4C: 'ReadPreferUnique',
      0x50: 'WriteNoSnpFullCleanSh',
      0x51: 'WriteNoSnpFullCleanInv',
      0x52: 'WriteNoSnpFullCleanShPerSep',
      0x54: 'WriteUniqueFullCleanSh',
      0x56: 'WriteUniqueFullCleanShPerSep',
      0x58: 'WriteBackFullCleanSh',
      0x59: 'WriteBackFullCleanInv',
      0x5A: 'WriteBackFullCleanShPerSep',
      0x5C: 'WriteCleanFullCleanSh',
      0x5E: 'WriteCleanFullCleanShPerSep',
      0x60: 'WriteNoSnpPtlCleanSh',
      0x61: 'WriteNoSnpPtlCleanInv',
      0x62: 'WriteNoSnpPtlCleanShPerSep',
      0x64: 'WriteUniquePtlCleanSh',
      0x66: 'WriteUniquePtlCleanShPerSep',
    }

    self.opc = self.syndrome['ERRLOGMAIN_HIGH'] & 0x7F
    if self.socket == 0:
      self.opc_str = opc_chi_req_dict.get(self.opc, 'reserved')
    elif self.socket == 1:
      self.opc_str = opc_nttp_dict.get(self.opc, 'reserved')
    else:
      self.opc_str = 'invalid'

  def decode_address(self):
    self.addrspace = (self.syndrome['ERRLOGADDR_HIGH'] >> 24) & 0x3F
    self.addr_lsb = self.syndrome['ERRLOGADDR_LOW']
    self.addr_msb = self.syndrome['ERRLOGADDR_HIGH'] & 0xFFFFFF
    self.addr = self.addr_lsb | (self.addr_msb << 32)

  def decode_errcode(self):
    self.code = (self.syndrome['ERRLOGMAIN_LOW'] >> 4) & 0xF
    self.code_str = ''
    if self.channel == 0:
      req_code_dict = {1: 'DEC'}
      self.code_str = req_code_dict.get(self.code, 'reserved')
    elif self.channel == 1:
      srsp_code_dict = {0: 'SLV NDERR'}
      self.code_str = srsp_code_dict.get(self.code, 'reserved')
    elif self.channel == 2:
      wdat_code_dict = {8: 'DERR'}
      self.code_str = wdat_code_dict.get(self.code, 'reserved')
    elif self.channel == 4:
      wdats_code_dict = {8: 'DERR, DEC'}
      self.code_str = wdats_code_dict.get(self.code, 'reserved')
    elif self.channel == 4 or self.channel == 5:
      nttp_code_dict = self.noc_data.get('errcodes', {})
      self.code_str = nttp_code_dict.get(self.code, 'reserved')

  def decode_misc(self):
    self.length = ((self.syndrome['ERRLOGMAIN_HIGH'] >> 8) & 0xFF) + 1
    self.excl = (self.syndrome['ERRLOGMAIN_HIGH'] >> 7) & 0x1
    nonsecure = {0: 'secure', 1: 'nonsecure'}
    self.nonsecure = (self.syndrome['ERRLOGADDR_HIGH'] >> 30) & 0x1
    self.nonsecure_str = nonsecure.get(self.nonsecure, 'invalid type')

# Main method which does decoding
def main():

  # Parsing the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("target", type = str, help = "Target number only")
  parser.add_argument("noc", type = str, help = "NoC that the error occurred on")
  parser.add_argument("ERRLOG0_LOW",  type = str, help = "ERRLOG0_LOW hexadecimal value (if not reported enter 0)")
  parser.add_argument("ERRLOG0_HIGH", type = str, help = "ERRLOG0_HIGH hexadecimal value (if not reported enter 0)")
  parser.add_argument("ERRLOG1_LOW",  type = str, help = "ERRLOG1_LOW hexadecimal value (if not reported enter 0)")
  parser.add_argument("ERRLOG1_HIGH", type = str, help = "ERRLOG1_HIGH hexadecimal value (if not reported enter 0)")
  parser.add_argument("ERRLOG2_LOW",  type = str, help = "ERRLOG2_LOW hexadecimal value (if not reported enter 0)")
  parser.add_argument("ERRLOG2_HIGH", type = str, help = "ERRLOG2_HIGH hexadecimal value (if not reported enter 0)")
  parser.add_argument("ERRLOG3_LOW",  type = str, help = "ERRLOG3_LOW hexadecimal value (if not reported enter 0)")
  parser.add_argument("ERRLOG3_HIGH", type = str, help = "ERRLOG3_HIGH hexadecimal value (if not reported enter 0)")
  parser.add_argument("FAULTINSTATUS0_LOW",  type = str, help = "FAULTINSTATUS0_LOW hexadecimal value (if not reported enter 0)")
  parser.add_argument("FAULTINSTATUS0_HIGH", type = str, help = "FAULTINSTATUS0_HIGH hexadecimal value (if not reported enter 0)")
  parser.add_argument("FAULTINSTATUS1_LOW",  type = str, help = "FAULTINSTATUS1_LOW hexadecimal value (if not reported enter 0)")
  parser.add_argument("FAULTINSTATUS1_HIGH", type = str, help = "FAULTINSTATUS1_HIGH hexadecimal value (if not reported enter 0)")
  args = parser.parse_args()

  # Need to convert ERRLOG values from strings to hexadecimal integers
  syndrome = defaultdict(lambda: defaultdict(dict))
  try:
    syndrome['obs']['ERRLOG0_LOW']         = int(args.ERRLOG0_LOW, 16)
    syndrome['obs']['ERRLOG0_HIGH']        = int(args.ERRLOG0_HIGH, 16)
    syndrome['obs']['ERRLOG1_LOW']         = int(args.ERRLOG1_LOW, 16)
    syndrome['obs']['ERRLOG1_HIGH']        = int(args.ERRLOG1_HIGH, 16)
    syndrome['obs']['ERRLOG2_LOW']         = int(args.ERRLOG2_LOW, 16)
    syndrome['obs']['ERRLOG2_HIGH']        = int(args.ERRLOG2_HIGH, 16)
    syndrome['obs']['ERRLOG3_LOW']         = int(args.ERRLOG3_LOW, 16)
    syndrome['obs']['ERRLOG3_HIGH']        = int(args.ERRLOG3_HIGH, 16)
    syndrome['sbm'][0]['FAULTINSTATUS0_LOW']  = int(args.FAULTINSTATUS0_LOW, 16)
    syndrome['sbm'][0]['FAULTINSTATUS0_HIGH'] = int(args.FAULTINSTATUS0_HIGH, 16)
    syndrome['sbm'][0]['FAULTINSTATUS1_LOW']  = int(args.FAULTINSTATUS1_LOW, 16)
    syndrome['sbm'][0]['FAULTINSTATUS1_HIGH'] = int(args.FAULTINSTATUS1_HIGH, 16)
  except ValueError:
    parser.print_help()
    return

  # Print the parameters that were passed
  print(("Target = %s" % args.target))
  print(("NoC = %s" % args.noc))
  print(("ERRLOG0_LOW           = 0x%x" % syndrome['obs']['ERRLOG0_LOW']))
  print(("ERRLOG0_HIGH          = 0x%x" % syndrome['obs']['ERRLOG0_HIGH']))
  print(("ERRLOG1_LOW           = 0x%x" % syndrome['obs']['ERRLOG1_LOW']))
  print(("ERRLOG1_HIGH          = 0x%x" % syndrome['obs']['ERRLOG1_HIGH']))
  print(("ERRLOG2_LOW           = 0x%x" % syndrome['obs']['ERRLOG2_LOW']))
  print(("ERRLOG2_HIGH          = 0x%x" % syndrome['obs']['ERRLOG2_HIGH']))
  print(("ERRLOG3_LOW           = 0x%x" % syndrome['obs']['ERRLOG3_LOW']))
  print(("ERRLOG3_HIGH          = 0x%x" % syndrome['obs']['ERRLOG3_HIGH']))
  print("SBM0:")
  print(("  FAULTINSTATUS0_LOW  = 0x%x" % syndrome['sbm'][0]['FAULTINSTATUS0_LOW']))
  print(("  FAULTINSTATUS0_HIGH = 0x%x" % syndrome['sbm'][0]['FAULTINSTATUS0_HIGH']))
  print(("  FAULTINSTATUS1_LOW  = 0x%x" % syndrome['sbm'][0]['FAULTINSTATUS1_LOW']))
  print(("  FAULTINSTATUS1_HIGH = 0x%x" % syndrome['sbm'][0]['FAULTINSTATUS1_HIGH']))

  try:
    decoding = NocDecoding(args.target, args.noc, syndrome)

    print(decoding)
  except DecodingError as e:
    print((str(e)))
    return

if __name__ == '__main__':
  main()