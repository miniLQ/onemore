#===========================================================================
#  Copyright (c) 2017 - 2018, 2021 Qualcomm Technologies, Inc.
#  All Rights Reserved.
#  Qualcomm Technologies Proprietary and Confidential
#===========================================================================
import collections
import os.path
from sys import argv
import argparse
import sys
from tempfile import gettempdir
try:
  parser_args = argparse.ArgumentParser(description='Process the input log file details.')
  optional = parser_args._action_groups.pop()
  required = parser_args.add_argument_group("required arguments")
  #check the arguments passed by user.
  required.add_argument('-t','--tz',
                      help='Location of tz build to pick dictionary',
                      required=True)
  required.add_argument('-l','--log',
                      help='Absolute Location of log file',
                      type=argparse.FileType('r'),
                      required=True)
  optional.add_argument('-e','--errs',
                      help='Location of error code dictionary')
  optional.add_argument('-o','--output',
                      help='Absolute Location of output file')
  optional.add_argument('-s','--stdout',
                      help='Option to disable printing on standard out. This is true by default. Pass False to disable',
                      default=True)
  parser_args._action_groups.append(optional)
  args = parser_args.parse_args()
  if args.tz is None and args.errs is None or args.log is None :
    parser_args.print_help()
    exit()
  if(os.path.isdir(args.tz)==False):
    raise argparse.ArgumentTypeError("{0} is not a valid path".format(args.tz))
  if(os.access(args.tz,os.R_OK)==False):
    raise argparse.ArgumentTypeError("{0} is not readable directory".format(args.tz))
  if args.errs is None :
    dict_txt=os.path.join(args.tz,'errorCodesDict.txt')
  else :
    dict_txt=args.errs
  if args.output is None :
    output_txt=os.path.join(gettempdir() , 'TZ_LOG_STR.txt')
  else :
    output_txt=args.output
  with args.log as logFile, open(output_txt, 'w') as outFile, open(dict_txt, 'r') as errCodesDictFile :
    '''create a collection from dictionary the first element is error code second element is the list containing value of error code and string.'''
    errCodeDict = collections.defaultdict(list)
    errorCodeDesc = {}
    errFatalDict = dict()
    fatal_codes = False
    errFatalMacroName = 'TZBSP_KRNL_FATAL_ERR_TYPE'
    for line in errCodesDictFile:
      '''generate a dictionary for error fatal codes.'''
      if  "Start Error Fatal Codes" in line:
        if 'for' in line:
          errFatalMacroName = line.split('for')[1].split('+')[0].strip()
        fatal_codes = True 
      if  "End Error Fatal Codes" in line:
        fatal_codes = False  
      if (fatal_codes and ':' in line):
        errFatalDict[line.split(':')[0].rstrip("\r\n")] =  line.split(':')[1].rstrip("\r\n")
      '''generate Error code dictionary.'''
      if ':' in line and (not fatal_codes)  :
        (errorCodeNumber,errorCodeString,errorCodeDesc)= line.strip().split(':',2)
        errCodeDict[errorCodeNumber].append(errorCodeString)
        if (errorCodeDesc) :
          errCodeDict[errorCodeNumber].append(errorCodeDesc)
    '''end creating a collection from dictionary--> errCodeDict
    write to the new file, converted strings
    each line is --> (600003a 10e 76048 0 100 0 0 20 ffffffff00000020 0)'''
    for line in logFile :
      line =line.strip()
      line = line.rstrip("\r\n")
      if '](' in line:
        timestamp=line.split('](')[0]
        line='('+  line.split('](')[1]
      '''if line has ( and ) at start and end we process it else print as it is'''
      if line[:1]=='(' and line[-1]==')' :
        errorCodeInLog=line.strip().split('(')[1]
        '''split each line with space to get list of error codes and args'''
        if ' ' in errorCodeInLog :
          arguments = line.replace(')', '').split(' ')
          errorCodeInLog = arguments[0]
          errorCodeInLog = errorCodeInLog.replace('(', '').strip()
          arguments.pop(0)
        else :
          arguments=')'
        '''remove any ) or space if present in errorCode'''
        errorCodeInLog = errorCodeInLog.replace(')', '').strip()
        '''list of format specifiers in C'''
        formatSpecifiers=['%X', '%x', '%c', '%d','%e', '%f', '%g', '%o', '%p',  '%u' , '%08x', '%16x']
        '''map all formart specifiers to %s, since we replace all format specifiers with %s'''
        mapping = { '%X':'%s', '%x':'%s', '%c':'%s', '%d':'%s','%e':'%s', '%f':'%s', '%g':'%s', '%o':'%s', '%p':'%s',  '%u':'%s', '%08x':'%s','%16x':'%s'}
        ''' get the error code value from dictionary -->errCodeDict[errorCodeInLog])'''
        if errorCodeInLog in errCodeDict :
          if (len(errCodeDict[errorCodeInLog]) >1) :
            stringValue=errCodeDict[errorCodeInLog][1].replace('\n', '')
          else:
            stringValue=' '
            stringValueOrig=''
          ''' if any format specifier is present convert it to %s and replace with arguments'''
          if any(fmtSpecifier in stringValue for fmtSpecifier in formatSpecifiers):
            stringValueOrig=stringValue
            for k, v in mapping.items():
              stringValue = stringValue.replace(k, v)
            ''' if count of format specifiers is not equal then don't error out hence check is added.'''
            if stringValue.count('%s')==len(arguments) :
              stringValue=stringValue % tuple(arguments)
              stringValue=" "+ stringValue             
            else :
              argsVal= " ".join((str(p) for p in arguments) )
              argsVal=argsVal.replace('\n', '')
              stringValue=" "+ argsVal +'  '+stringValueOrig
          if  stringValue == ' ' and    len(arguments)>0 :
            argsVal= " ".join((str(p) for p in arguments) )
            argsVal=argsVal.replace('\n', '')
            stringValue=" "+ argsVal +'  '+stringValueOrig
          '''Process error fatal codes'''
          if errFatalMacroName in errCodeDict[errorCodeInLog][0] and ':' in stringValue:
            errFatalCode =  stringValue.split(':')[1].strip()
            errFatalCode = int(errFatalCode,16)
            if str(errFatalCode) in errFatalDict :
              stringValue = stringValue.split(':')[0]+ ':' +errFatalDict[str(errFatalCode)]
          
          outFile.write(timestamp +']('+errCodeDict[errorCodeInLog][0]+stringValue +')'+'\n')
          if args.stdout==True :
            print((timestamp +']('+errCodeDict[errorCodeInLog][0]+stringValue +')'+'\n'))
        else :
          outFile.write(timestamp +']'+line+ '\n')
          if args.stdout==True :
            print((timestamp +']'+line+ '\n'))
      else:
        outFile.write(line+ '\n')
        if args.stdout==True :
          print((line+ '\n'))
    
    print("The output file is at: "+outFile.name)
    exit(0)
except Exception as e:
  #taceback.print_exc(file = sys.stderr)
  print(e)
  exit(1)