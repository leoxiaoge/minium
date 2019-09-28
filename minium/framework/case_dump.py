#!/usr/bin/env python3
import argparse
import os.path
import sys
import json
import logging
from minium.framework import case_inspect
logger=logging.getLogger()
def main():
 parsers=argparse.ArgumentParser()
 parsers.add_argument("-i","--input",dest="input_path",type=str,required=True,help="case directory",)
 parsers.add_argument("-f","--format",dest="format",type=str,help="output json",choices=["console","json"],default="console",)
 parsers.add_argument("-p","--path",dest="path",type=str,help="result output path")
 parser_args=parsers.parse_args()
 input_path=parser_args.input_path
 format_type=parser_args.format
 if not os.path.exists(input_path)or not os.path.isdir(input_path):
  raise RuntimeError("case directory: %s not exists"%input_path)
 sys.path.insert(0,parser_args.input_path)
 test_cases=case_inspect.load_module(input_path)
 if format_type=="console":
  print(json.dumps(test_cases,indent=4))
 elif format_type=="json":
  path=parser_args.path
  json.dump(test_cases,open(path,"rb"),indent=4)
if __name__=="__main__":
 main()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
