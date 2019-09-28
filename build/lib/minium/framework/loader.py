#!/usr/bin/env python3
import sys
import os.path
import argparse
import unittest
import logging
import logging.handlers
import json
import glob
import fnmatch
from minium import build_version
from minium.framework import case_inspect
from minium.framework import minitest
from minium.framework import assertbase
from minium.framework import miniconfig
from minium.framework import miniresult
from minium.framework import report
logger=logging.getLogger()
FILENAME_SUMMARY="summary.json"
def run_tests(tests):
 result=miniresult.MiniResult()
 tests.run(result)
 result.print_shot_msg()
 return result
def load_from_suite(case_path,json_path):
 json_suite=json.load(open(json_path,"rb"))
 tests=unittest.TestSuite()
 module_case_info_list=case_inspect.load_module(case_path)
 for pkg_cases in json_suite["pkg_list"]:
  pkg=pkg_cases["pkg"]
  case_list=pkg_cases["case_list"]
  true_pkg_list=[]
  for module_name,module_info in module_case_info_list.items():
   if fnmatch.fnmatch(module_name,pkg):
    for case_info in module_info["case_list"]:
     for case_name in case_list:
      if fnmatch.fnmatch(case_info["name"],case_name):
       _=load_from_case_name(module_name,case_info["name"])
       tests.addTests(_)
    true_pkg_list.append(module_name)
 return tests
def load_from_pkg(pkg):
 loader=unittest.TestLoader()
 test_module=case_inspect.import_module(pkg)
 tests=loader.loadTestsFromModule(test_module)
 return tests
def load_from_case_name(pkg,case_name):
 loader=unittest.TestLoader()
 test_class=case_inspect.find_test_class(pkg,case_name)
 if test_class:
  return loader.loadTestsFromName(case_name,test_class)
 else:
  raise AssertionError("can't not find testcase %s in pkg %s"%(case_name,pkg))
def main():
 parsers=argparse.ArgumentParser()
 parsers.add_argument("-v","--version",dest="version",action="store_true",default=False)
 parsers.add_argument("-t","--path",dest="path",type=str,help="case directory, default current directory",default=None)
 parsers.add_argument("-p","--pkg",dest="pkg",type=str,help="case package name")
 parsers.add_argument("-c","--case",dest="case_name",type=str,default=None,help="case name")
 parsers.add_argument("-k","--apk",dest="apk",action="store_true",default=False,help="show apk path")
 parsers.add_argument("-s","--suite",dest="suite_path",type=str,default=None,help="test suite file, a json format file",)
 parsers.add_argument("-f","--config",dest="config",type=str,default=None,help="config file path")
 parsers.add_argument("-g","--generate",dest="generate",action="store_true",default=False,help="generate html report")
 parsers.format_help()
 parser_args=parsers.parse_args()
 version=parser_args.version
 path=parser_args.path
 pkg=parser_args.pkg
 apk=parser_args.apk
 case_name=parser_args.case_name
 generate_report=parser_args.generate
 suite_path=parser_args.suite_path
 config=parser_args.config
 if version:
  print(build_version())
  exit(0)
 if apk:
  bin_root=os.path.join(os.path.dirname(os.path.dirname(__file__)),"native","lib","at","bin","*apk")
  print("please install apk:")
  for filename in glob.glob(bin_root):
   print(f"adb install -r {filename}")
  exit(0)
 if path is None:
  path=os.getcwd()
 if not os.path.exists(path)or not os.path.isdir(path):
  logger.error("case directory: %s not exists"%path)
  parsers.print_help()
  exit(0)
 sys.path.insert(0,path)
 if config and not os.path.exists(config):
  logger.error("config not exists:%s"%config)
  parsers.print_help()
  exit(0)
 if config:
  minitest.AssertBase.CONFIG=miniconfig.MiniConfig.from_file(config)
 minitest.AssertBase.setUpConfig()
 minitest.is_share_ide=True
 assertbase.g_from_command=True
 if suite_path:
  tests=load_from_suite(path,suite_path)
 elif pkg is None:
  logger.error("need suite_path or pkg")
  parsers.print_help()
  exit(0)
 elif case_name is None:
  tests=load_from_pkg(pkg)
 else:
  tests=load_from_case_name(pkg,case_name)
 try:
  result=run_tests(tests)
  summary_path=os.path.join(minitest.AssertBase.CONFIG.outputs,FILENAME_SUMMARY)
  result.dumps(summary_path)
  if generate_report:
   report.imp_main(minitest.AssertBase.CONFIG.outputs)
 except:
  logger.exception("not catch exception")
  minitest.release_minium(minitest.AssertBase.CONFIG)
if __name__=="__main__":
 main()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
