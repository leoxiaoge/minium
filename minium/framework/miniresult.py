#!/usr/bin/env python3
import unittest
import json
class MiniResult(unittest.TestResult):
 def __init__(self):
  super(MiniResult,self).__init__()
  self.summary={"test_num":0,"errors":[],"failures":[],"class_errors":[],"class_failures":[]}
 def finish(self):
  self.summary["test_num"]=self.testsRun
  def format_error_info(_error):
   test_case=_error[0]
   if isinstance(test_case,unittest.TestCase):
    return{"module":test_case.__class__.__name__,"error_type":"test_case","case_name":test_case._testMethodName,"exception":_error[1]}
   else:
    print("setupClass or tearDownClass failed")
    return{"error_type":"test_class","exception":_error[1],"description":test_case.description}
  for error in self.errors:
   format_info=format_error_info(error)
   if format_info["error_type"]=="test_case":
    self.summary["errors"].append(format_info)
   elif format_info["error_type"]=="test_class":
    self.summary["class_errors"].append(format_info)
  for failure in self.failures:
   format_info=format_error_info(failure)
   if format_info["error_type"]=="test_case":
    self.summary["failures"].append(format_info)
   elif format_info["error_type"]=="test_class":
    self.summary["class_failures"].append(format_info)
 def print_shot_msg(self):
  self.finish()
  title=f"case num:{self.summary['test_num']}, failed num:{len(self.summary['errors'])}, error num:{len(self.summary['failures'])}"
  title="="*20+title+"="*20
  print(title)
  for error in self.summary["errors"]:
   print(f"{error['module']}:{error['case_name']} has error:")
   print(error["exception"])
   print("-"*len(title))
  for error in self.summary["failures"]:
   print(f"{error['module']}:{error['case_name']} has failure:")
   print(error["exception"])
   print("-"*len(title))
  for error in self.summary["class_errors"]:
   print(f"{error['description']} has error:")
   print(error["exception"])
   print("-"*len(title))
  for error in self.summary["class_failures"]:
   print(f"{error['description']} has failure:")
   print(error["exception"])
   print("-"*len(title))
 def dumps(self,filename):
  json.dump(self.summary,open(filename,"w"))
class Test1(unittest.TestCase):
 def test_1(self):
  self.assertTrue(True)
 def test_2(self):
  self.assertTrue(False,"failed")
class Test2(unittest.TestCase):
 def setUp(self):
  raise RuntimeError("setup failed")
 def test_1(self):
  self.assertTrue(True)
 def test_2(self):
  self.assertTrue(False,"failed")
if __name__=='__main__':
 loader=unittest.TestLoader()
 tests=loader.loadTestsFromTestCase(Test1)
 tests1=loader.loadTestsFromTestCase(Test2)
 tests.addTests(tests1)
 result=MiniResult()
 tests.run(result)
 result.print_shot_msg()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
