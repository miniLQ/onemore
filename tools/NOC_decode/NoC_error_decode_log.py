from collections import defaultdict
import argparse, re
import NoC_error_decode as noc_decoder
import DDRSS_error_decode as ddrss_decoder

obs_keys = ['ERRLOG0_LOW', 'ERRLOG0_HIGH', 'ERRLOG1_LOW', 'ERRLOG1_HIGH', 'ERRLOG2_LOW', 'ERRLOG2_HIGH', 'ERRLOG3_LOW', 'ERRLOG3_HIGH']
sbm_keys = ['FAULTINSTATUS0_LOW', 'FAULTINSTATUS0_HIGH', 'FAULTINSTATUS1_LOW', 'FAULTINSTATUS1_HIGH']
poc_keys = ['ERRSTATUS_LOW', 'ERRLOGMAIN_LOW', 'ERRLOGMAIN_HIGH', 'ERRLOGADDR_LOW', 'ERRLOGADDR_HIGH', 'ERRLOGUSER_LOW', 'ERRLOGUSER_HIGH']
ddrsserr_feac_keys = [ 'FEAC_DEC_ERR_STATUS1', 'FEAC_DEC_ERR_STATUS2', 'FEAC_DEC_ERR_STATUS3', 'FEAC_DEC_ERR_STATUS3', 'FEAC_DEC_ERR_STATUS4', 'FEAC_DEC_ERR_STATUS5']

def parse_log_file(f):
  # Deal with aliases that may not match xml
  aliases = { 'A1NOC' : 'aggre1_noc',
              'A2NOC' : 'aggre2_noc', }

  errlog = re.compile('.+?(?P<noc>[A-Z0-9_]+) ERROR: (SBM(?P<sbm>\d+) )*(?P<reg>\w+) = (?P<val>\w+)')
  err_syn = re.compile('.+?70023c (?P<noc>[A-Z0-9_]+) (?P<ERRLOG0_LOW>[a-f0-9]+) (?P<ERRLOG0_HIGH>[a-f0-9]+) ' \
                       '(?P<ERRLOG1_LOW>[a-f0-9]+) (?P<ERRLOG1_HIGH>[a-f0-9]+) (?P<ERRLOG2_LOW>[a-f0-9]+) (?P<ERRLOG2_HIGH>[a-f0-9]+) ' \
                       '(?P<ERRLOG3_LOW>[a-f0-9]+) (?P<ERRLOG3_HIGH>[a-f0-9]+) (?P<ERRLOG2_1_LOW>[a-f0-9]+) (?P<ERRLOG2_1_HIGH>[a-f0-9]+) ' \
                       '(?P<ERRLOG4_3_LOW>[a-f0-9]+) (?P<ERRLOG4_3_HIGH>[a-f0-9]+) (?P<ERRLOG6_5_LOW>[a-f0-9]+) (?P<ERRLOG6_5_HIGH>[a-f0-9]+) ' \
                       '(?P<ERRLOG8_HIGH>[a-f0-9]+)')
  err_sbm = re.compile('.+?70023d (?P<noc>[A-Z0-9_]+) (?P<sbm>\d+) (?P<FAULTINSTATUS0_LOW>[a-f0-9]+) (?P<FAULTINSTATUS0_HIGH>[a-f0-9]+) ' \
                       '(?P<FAULTINSTATUS1_LOW>[a-f0-9]+) (?P<FAULTINSTATUS1_HIGH>[a-f0-9]+)')
  err_syn_parsed = re.compile('.+?Details: (?P<noc>[A-Z0-9_]+).+?0x(?P<ERRLOG0_LOW>[a-f0-9]+).+?0x(?P<ERRLOG0_HIGH>[a-f0-9]+)' \
                       '.+?0x(?P<ERRLOG1_LOW>[a-f0-9]+).+?0x(?P<ERRLOG1_HIGH>[a-f0-9]+).+?0x(?P<ERRLOG2_LOW>[a-f0-9]+).+?0x(?P<ERRLOG2_HIGH>[a-f0-9]+)' \
                       '.+?0x(?P<ERRLOG3_LOW>[a-f0-9]+).+?0x(?P<ERRLOG3_HIGH>[a-f0-9]+).+?0x(?P<ERRLOG2_1_LOW>[a-f0-9]+).+?0x(?P<ERRLOG2_1_HIGH>[a-f0-9]+)' \
                       '.+?0x(?P<ERRLOG4_3_LOW>[a-f0-9]+).+?0x(?P<ERRLOG4_3_HIGH>[a-f0-9]+).+?0x(?P<ERRLOG6_5_LOW>[a-f0-9]+).+?0x(?P<ERRLOG6_5_HIGH>[a-f0-9]+)' \
                       '.+?0x(?P<ERRLOG8_HIGH>[a-f0-9]+)')
  err_sbm_parsed = re.compile('.+?NOC_NAME: (?P<noc>[A-Z0-9_]+) SBM:(?P<sbm>\d+),.+?0x(?P<FAULTINSTATUS0_LOW>[a-f0-9]+).+?0x(?P<FAULTINSTATUS0_HIGH>[a-f0-9]+)' \
                       '.+?0x(?P<FAULTINSTATUS1_LOW>[a-f0-9]+).+?0x(?P<FAULTINSTATUS1_HIGH>[a-f0-9]+)')
  err_poc = re.compile('.+?700391 (?P<noc>[A-Z0-9_]+) (?P<poc>\d+) (?P<ERRSTATUS_LOW>[a-f0-9]+) (?P<ERRLOGMAIN_LOW>[a-f0-9]+) ' \
                       '(?P<ERRLOGMAIN_HIGH>[a-f0-9]+) (?P<ERRLOGADDR_LOW>[a-f0-9]+) (?P<ERRLOGADDR_HIGH>[a-f0-9]+) ' \
                       '(?P<ERRLOGUSER_LOW>[a-f0-9]+) (?P<ERRLOGUSER_HIGH>[a-f0-9]+)')
  err_poc_parsed = re.compile('.+?NOC_NAME: (?P<noc>[A-Z0-9_]+) POC:(?P<poc>\d+),.+?0x(?P<ERRSTATUS_LOW>[a-f0-9]+).+?0x(?P<ERRLOGMAIN_LOW>[a-f0-9]+)' \
                       '.+?0x(?P<ERRLOGMAIN_HIGH>[a-f0-9]+).+?0x(?P<ERRLOGADDR_LOW>[a-f0-9]+).+?0x(?P<ERRLOGADDR_HIGH>[a-f0-9]+)' \
                       '.+?0x(?P<ERRLOGUSER_LOW>[a-f0-9]+).+?0x(?P<ERRLOGUSER_HIGH>[a-f0-9]+)')

  err_ddrss_parsed = re.compile('.+?DDRSSERR: (?P<llcc>LLCC[0-9]+) (?P<fe>FE..).*?_STATUS1.+?0x(?P<ERR_STATUS1>[a-fA-F0-9]+).+?0x(?P<ERR_STATUS2>[a-fA-F0-9]+).+?0x(?P<ERR_STATUS3>[a-fA-F0-9]+).+?0x(?P<ERR_STATUS4>[a-fA-F0-9]+).+?0x(?P<ERR_STATUS5>[a-fA-F0-9]+)')
  err_ddrss_feac_raw = re.compile('.+?70026d (?P<llcc>LLCC[0-9]+) (?P<ERR_STATUS1>[a-fA-F0-9]+) (?P<ERR_STATUS2>[a-fA-F0-9]+) (?P<ERR_STATUS3>[a-fA-F0-9]+) (?P<ERR_STATUS4>[a-fA-F0-9]+) (?P<ERR_STATUS5>[a-fA-F0-9]+)')
  err_ddrss_fewc_raw = re.compile('.+?70026c (?P<llcc>LLCC[0-9]+) (?P<ERR_STATUS1>[a-fA-F0-9]+) (?P<ERR_STATUS2>[a-fA-F0-9]+) (?P<ERR_STATUS3>[a-fA-F0-9]+) (?P<ERR_STATUS4>[a-fA-F0-9]+) (?P<ERR_STATUS5>[a-fA-F0-9]+)')

  # FEAC raw [0754d4b88](70026d LLCC0 62000000 10000 61 c1 1800)
  # FEAC sample [05daecbfa](DDRSSERR_FEAC_DEC_ERR_STATUS_REG DDRSSERR: LLCC0 FEAC_DEC_ERR_STATUS1 = 0xac0000 FEAC_DEC_ERR_STATUS2 = 0x1311e FEAC_DEC_ERR_STATUS3 = 0x3b FEAC_DEC_ERR_STATUS4 = 0xc1 FEAC_DEC_ERR_STATUS5 = 0x1800)
  # FEWC raw [05daecbfa](70026d LLCC0 ac0000 1311e 3b c1 1800)
  # FEWC sample 67.524134:   DDRSSERR_FEWC_STATUS_REG : DDRSSERR: LLCC0 FEWC_STATUS1 = 0x00000003 FEWC_STATUS2 = 0x00560000 FEWC_STATUS3 = 0x0000451e FEWC_STATUS4 = 0x00000032 FEWC_STATUS5 = 0x00016818

  err_mcerr_parsed = re.compile('.+?DDRS_MC.*(?P<mc>MC[0-9]+).+?0x(?P<ESYN_0>[a-fA-F0-9]+).+?0x(?P<ESYN_1>[a-fA-F0-9]+)')
  err_mcerr_raw    = re.compile('.+?70026e (?P<mc>MC[0-9]+) (?P<ESYN_0>[a-fA-F0-9]+) (?P<ESYN_1>[a-fA-F0-9]+)')
  # [0754d4b88](70026e MC1 e5000000 e5111111)
  # [0754d4b88](DDRS_MC_ADDR_DECERR_EYN  DDRS MC MC1 ERROR: CABO_ADDR_DECERR_ESYN_0 = 0xe5000000 CABO_ADDR_DECERR_ESYN_1 = 0xe5111111

  errors = []
  cache = defaultdict(lambda: defaultdict(dict))

  for (line_num, line) in enumerate(list(f)):
    # Default TZ log format (uncompressed)
    if err_mcerr_raw.match(line):
      # MC errors need to come first because errlog accidentally matches
      match = err_mcerr_raw.match(line).groupdict()
      match['line_num'] = line_num
      errors.append({'mc':match['mc'].lower(), 'regs':match})
    elif err_mcerr_parsed.match(line):
      # MC errors need to come first because errlog accidentally matches
      match = err_mcerr_parsed.match(line).groupdict()
      match['line_num'] = line_num
      errors.append({'mc':match['mc'].lower(), 'regs':match})

    elif errlog.match(line):
      match = errlog.match(line).groupdict()
      noc = aliases.get(match['noc'], match['noc'])

      # Check for duplicate NoC error and push
      if match['reg'] in obs_keys:
        if match['reg'] in cache.get(noc.lower(),{}).get('obs',{}):
          errors.append({'noc':noc.lower(), 'regs':cache.pop(noc.lower())})
        cache[noc.lower()]['obs'][match['reg']] = int(match['val'],16)
        cache[noc.lower()]['line_num'] = line_num
      elif match['reg'] in sbm_keys:
        sbm = int(match['sbm'],16)
        if match['reg'] in cache.get(noc.lower(),{}).get('sbm',{}):
          errors.append({'noc':noc.lower(), 'regs':cache.pop(noc.lower())})
        if sbm not in cache[noc.lower()]['sbm']:
          cache[noc.lower()]['sbm'][sbm] = {}
        cache[noc.lower()]['sbm'][sbm].update({match['reg']: int(match['val'],16)})
        cache[noc.lower()]['line_num'] = line_num

    # Compressed and unparsed formats
    elif err_syn.match(line):
      match = err_syn.match(line).groupdict()
      noc = aliases.get(match['noc'], match['noc'])

      # Check for duplicate NoC error and push
      # This means previous obs log *or* sbm as SBM is logged first in sw
      if 'obs' in cache.get(noc.lower(),{}) or 'sbm' in cache.get(noc.lower(),{}):
        errors.append({'noc':noc.lower(), 'regs':cache.pop(noc.lower())})
      match = {k: int(v,16) for k,v in list(match.items()) if k !='noc'}
      cache[noc.lower()]['obs'] = match
      cache[noc.lower()]['line_num'] = line_num

    elif err_sbm.match(line):
      match = err_sbm.match(line).groupdict()
      noc = aliases.get(match['noc'], match['noc'])

      # Check for duplicate NoC error and push
      sbm = int(match['sbm'],16)
      if sbm in cache.get(noc.lower(),{}).get('sbm',{}):
        errors.append({'noc':noc.lower(), 'regs':cache.pop(noc.lower())})
      match = {k: int(v,16) for k,v in list(match.items()) if k !='noc' and k != 'sbm'}
      cache[noc.lower()]['sbm'].update({sbm: match})
      cache[noc.lower()]['line_num'] = line_num

    # Compressed but parsed formats
    elif err_syn_parsed.match(line):
      match = err_syn_parsed.match(line).groupdict()
      noc = aliases.get(match['noc'], match['noc'])

      # Check for duplicate NoC error and push
      # This means previous obs log *or* sbm as SBM is logged first in sw
      if 'obs' in cache.get(noc.lower(),{}) or 'sbm' in cache.get(noc.lower(),{}):
        errors.append({'noc':noc.lower(), 'regs':cache.pop(noc.lower())})
      match = {k: int(v,16) for k,v in list(match.items()) if k !='noc'}
      cache[noc.lower()]['obs'] = match
      cache[noc.lower()]['line_num'] = line_num

    elif err_sbm_parsed.match(line):
      match = err_sbm_parsed.match(line).groupdict()
      noc = aliases.get(match['noc'], match['noc'])

      # Check for duplicate NoC error and push
      sbm = int(match['sbm'],16)
      if sbm in cache.get(noc.lower(),{}).get('sbm',{}):
        errors.append({'noc':noc.lower(), 'regs':cache.pop(noc.lower())})
      match = {k: int(v,16) for k,v in list(match.items()) if k !='noc' and k != 'sbm'}
      cache[noc.lower()]['sbm'].update({sbm: match})
      cache[noc.lower()]['line_num'] = line_num

    elif err_poc.match(line):
      match = err_poc.match(line).groupdict()
      noc = aliases.get(match['noc'], match['noc'])
      poc = int(match['poc'],16)
      regs = {k: int(v,16) for k,v in list(match.items()) if k != 'noc' and k != 'poc'}
      regs['line_num'] = line_num

      errors.append({'noc':noc.lower(), 'poc':poc, 'regs':regs})

    elif err_poc_parsed.match(line):
      match = err_poc_parsed.match(line).groupdict()
      noc = aliases.get(match['noc'], match['noc'])
      poc = int(match['poc'],16)
      regs = {k: int(v,16) for k,v in list(match.items()) if k != 'noc' and k != 'poc'}
      regs['line_num'] = line_num

      errors.append({'noc':noc.lower(), 'poc':poc, 'regs':regs})

    elif err_ddrss_parsed.match(line):
      match = err_ddrss_parsed.match(line).groupdict()
      match['line_num'] = line_num
      errors.append({match['fe'].lower() : match['llcc'].lower(), 'regs':match})
    elif err_ddrss_feac_raw.match(line):
      match = err_ddrss_feac_raw.match(line).groupdict()
      match['fe'] = 'FEAC'
      match['line_num'] = line_num
      errors.append({match['fe'].lower() : match['llcc'].lower(), 'regs':match})
    elif err_ddrss_fewc_raw.match(line):
      match = err_ddrss_fewc_raw.match(line).groupdict()
      match['fe'] = 'FEWC'
      match['line_num'] = line_num
      errors.append({match['fe'].lower() : match['llcc'].lower(), 'regs':match})

  # Pop everything out of the dictionary.
  for k,v in list(cache.items()):
    errors.append({'noc':k, 'regs':v})

  # Order the errors by the line numbers, line_num is the last line this error was seen on in the log.
  errors = sorted(errors, key=lambda d: d['regs']['line_num'])

  return errors

def output(s):
  global args

  if args.output:
    args.output.write(s + '\n')
  else:
    print(s)

def decode_noc_error(error):
  noc = error['noc']
  regs = error['regs']
  obs_parsed = len(regs['obs']) > 0
  regs['obs'] = {key: regs.get('obs',{}).get(key,0) for key in obs_keys}
  regs['sbm'] = regs.get('sbm',{0:{}})
  for inst in regs['sbm']:
    regs['sbm'][inst] = {key: regs['sbm'][inst].get(key,0) for key in sbm_keys}

    decoding = noc_decoder.NocDecoding(args.target, noc, regs)

    # Print the parameters that were passed
    output("*******************************")
    output("NoC = %s" % noc)
    if obs_parsed:
      output("ERRLOG0_LOW           = 0x%x" % regs['obs']['ERRLOG0_LOW'])
      output("ERRLOG0_HIGH          = 0x%x" % regs['obs']['ERRLOG0_HIGH'])
      output("ERRLOG1_LOW           = 0x%x" % regs['obs']['ERRLOG1_LOW'])
      output("ERRLOG1_HIGH          = 0x%x" % regs['obs']['ERRLOG1_HIGH'])
      output("ERRLOG2_LOW           = 0x%x" % regs['obs']['ERRLOG2_LOW'])
      output("ERRLOG2_HIGH          = 0x%x" % regs['obs']['ERRLOG2_HIGH'])
      output("ERRLOG3_LOW           = 0x%x" % regs['obs']['ERRLOG3_LOW'])
      output("ERRLOG3_HIGH          = 0x%x" % regs['obs']['ERRLOG3_HIGH'])
    for inst in regs['sbm']:
      output("SBM%d:" % inst)
      output("  FAULTINSTATUS0_LOW  = 0x%x" % regs['sbm'][inst]['FAULTINSTATUS0_LOW'])
      output("  FAULTINSTATUS0_HIGH = 0x%x" % regs['sbm'][inst]['FAULTINSTATUS0_HIGH'])
      output("  FAULTINSTATUS1_LOW  = 0x%x" % regs['sbm'][inst]['FAULTINSTATUS1_LOW'])
      output("  FAULTINSTATUS1_HIGH = 0x%x" % regs['sbm'][inst]['FAULTINSTATUS1_HIGH'])
    output(repr(decoding))

def decode_poc_error(error):
  noc = error['noc']
  regs = error['regs']
  index = error['poc']

  decoding = noc_decoder.PocDecoding(args.target, noc, index, regs)

  output("*******************************")
  output("NoC = %s, PoC = %d" % (noc, index))
  output("ERRSTATUS_LOW   = 0x%x" % regs['ERRSTATUS_LOW'])
  output("ERRLOGMAIN_LOW  = 0x%x" % regs['ERRLOGMAIN_LOW'])
  output("ERRLOGMAIN_HIGH = 0x%x" % regs['ERRLOGMAIN_HIGH'])
  output("ERRLOGADDR_LOW  = 0x%x" % regs['ERRLOGADDR_LOW'])
  output("ERRLOGADDR_HIGH = 0x%x" % regs['ERRLOGADDR_HIGH'])
  output("ERRLOGUSER_LOW  = 0x%x" % regs['ERRLOGUSER_LOW'])
  output("ERRLOGUSER_HIGH = 0x%x" % regs['ERRLOGUSER_HIGH'])
  output(repr(decoding))

# Main method which does decoding
def main():
  global args

  # Parsing the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("target", type = str, help = "Target number only")
  parser.add_argument("log", type = str, help = "NoC that the error occurred on")
  parser.add_argument('-o','--output', help='Absolute location of output file', type=argparse.FileType('w'))
  args = parser.parse_args()

  # Read in the log file.
  try:
    with open(args.log, 'r') as f:
      errors = parse_log_file(f)
  except IOError as e:
    print((str(e)))
    return

  output("Target = %s" % args.target)
  for error in errors:
    try:
      if 'noc' in error:
        if 'ERRSTATUS_LOW' in error['regs']:
          decode_poc_error(error)
        else:
          decode_noc_error(error)
      elif 'mc' in error:
        output("MC decode not supported.")
        output("  %s" % error['regs']['mc'])
        output("  ESYN0 = %s" % error['regs']['ESYN_0'])
        output("  ESYN1 = %s" % error['regs']['ESYN_1'])

      elif 'feac' in error:
        decoding = ddrss_decoder.DDRSS_FEAC_Decoding(args.target, error['regs']['llcc'], error['regs'])
        output(str(decoding))

      elif 'fewc' in error:
        decoding = ddrss_decoder.DDRSS_FEWC_Decoding(args.target, error['regs']['llcc'], error['regs'])
        output(str(decoding))

      else:
        print(("UNKNOWN ERROR TYPE", error))

    except LookupError as e:
      # Bad target error, skip the rest
      print((str(e)))
      return
    except noc_decoder.DecodingError as e:
      # Decoding error, print and continue.
      print((str(e)))

if __name__ == '__main__':
  main()
