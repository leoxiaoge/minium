import unittest
import datetime
import json
import os.path
import inspect
import time
import logging
import logging.handlers
import traceback
import datetime
import re
from.miniconfig import MiniConfig,get_log_level
logger=logging.getLogger()
WORKSPACE_DIR=os.path.abspath(os.getcwd())
LOG_FORMATTER="%(levelname)-5.5s %(asctime)s %(filename)-10s %(funcName)-15s %(lineno)-3d %(message)s"
FILENAME_LOGGER="loader{0}.log".format(datetime.datetime.now().strftime("%Y%m%d"))
g_console_handler=None
g_case_log_handler=None
g_from_command=False
class AssertBase(unittest.TestCase):
 DEVICE_INFO={}
 CONFIG=None
 def setUp(self):
  super(AssertBase,self).setUp()
  self._log_filename=None
  self.test_config:MiniConfig=None 
  self.setup_time=time.time()
  self._setup_config()
  self._setup_log()
  self.assert_list=list()
  self.screen_when_check=False
  self.check_list=[]
  self.screen_info=[]
  self.__assert_index=0
  self._console_handle=None
  self._log_handle=None
  self._has_assert_error=False
  desc=self._testMethodDoc
  if desc is not None:
   lines=desc.split("\n")
   lines=[l.strip()for l in lines if l]
   desc="\n".join(lines)
  module_filename=inspect.getsourcefile(self.__class__)
  self._test_filename=module_filename
  module_name=None
  if module_filename:
   module_filename=os.sep.join(module_filename.split(".")[:-1])
   tokens=module_filename.split(os.sep)
   if len(tokens)==1:
    tokens=module_filename.split("/")
   root_package_name=os.path.abspath(__file__).split(os.sep)[-3]
   if root_package_name in tokens:
    index=tokens.index(root_package_name)
    module_name=".".join(tokens[index+2:])
   else:
    module_name=".".join(tokens) 
  self.results={"case_name":self._testMethodName,"run_time":str(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")),"test_type":self.__class__.__name__,"case_doc":desc,"success":False,"failures":"","errors":"","start_timestamp":self.setup_time,"is_failure":False,"is_error":False,"module":module_name,"failed_line_num":-1,"device":AssertBase.DEVICE_INFO,"log_filename":self._log_filename,}
 @classmethod
 def setUpConfig(cls):
  if cls.CONFIG is None:
   default_config_filename=os.path.join(WORKSPACE_DIR,"config.json")
   if os.path.exists(default_config_filename):
    cls.CONFIG=MiniConfig.from_file(default_config_filename)
   else:
    logger.warning("default configure file did not exist! use default config")
    cls.CONFIG=MiniConfig()
  if cls.CONFIG.outputs is None:
   outputs=os.path.join(os.getcwd(),"outputs")
   if not os.path.exists(outputs):
    os.makedirs(outputs)
   cls.CONFIG.outputs=outputs
  global g_console_handler,g_case_log_handler
  log_level=get_log_level(cls.CONFIG.debug_mode)
  if g_console_handler is None:
   console_handler=logging.StreamHandler()
   formatter=logging.Formatter(LOG_FORMATTER)
   console_handler.setFormatter(formatter)
   logger.addHandler(console_handler)
   logger.setLevel(log_level)
   g_console_handler=console_handler
  if g_case_log_handler is None:
   log_path=os.path.join(cls.CONFIG.outputs,FILENAME_LOGGER)
   case_log_handler=logging.handlers.RotatingFileHandler(log_path,maxBytes=1024*1024,encoding="utf-8")
   formatter=logging.Formatter(LOG_FORMATTER)
   case_log_handler.setFormatter(formatter)
   case_log_handler.setLevel(logging.DEBUG)
   logger.addHandler(case_log_handler)
   logger.setLevel(log_level)
   g_case_log_handler=case_log_handler
 @classmethod
 def setUpClass(cls):
  cls.setUpConfig()
 def _setup_config(self):
  self.test_config=MiniConfig(self.CONFIG)
  dt=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
  self.test_config.case_output=os.path.join(self.test_config.outputs,self._testMethodName,dt)
  if not os.path.exists(self.test_config.case_output):
   os.makedirs(self.test_config.case_output)
 def _setup_log(self):
  case_log_filename=self.wrap_filename("{0}.log".format(self._testMethodName))
  self._log_filename=os.path.basename(case_log_filename)
  case_log_handler=logging.handlers.RotatingFileHandler(case_log_filename,maxBytes=1024*1024,encoding="utf-8")
  formatter=logging.Formatter(LOG_FORMATTER)
  case_log_handler.setFormatter(formatter)
  self._case_log_handler=case_log_handler
  logger.addHandler(self._case_log_handler)
  logger.info(self.CONFIG)
 def _teardown_collect(self):
  sys_info=self._outcome.errors[-1][-1]
  test_method=getattr(self,self._testMethodName)
  source_line=inspect.getsourcelines(test_method)
  self.results["source"]={"code":source_line[0],"start":source_line[1]}
  if sys_info:
   e_type,e_value,e_traceback=sys_info
   self.results["failed_line_num"]=-1
   stack_lines=traceback.format_exception(e_type,e_value,e_traceback)
   logger.exception("assert failed",exc_info=sys_info)
   if len(stack_lines)>2:
    r=re.compile(r"File [\'\"](.*)[\'\"], line (\d+), in (\w+)")
    for stack_line in stack_lines[1:]:
     m=r.search(stack_line)
     if m:
      if(m.group(1)==self._test_filename and m.group(3)==self._testMethodName):
       self.results["failed_line_num"]=int(m.group(2))
   if self._has_assert_error:
    self.results["failures"]="".join(stack_lines)
    self.results["is_failure"]=True
   else:
    self.results["errors"]="".join(stack_lines)
    self.results["is_error"]=True
  else:
   self.results["success"]=True
 def _teardown_collect_other(self):
  self.results["stop_timestamp"]=time.time()
  self.results["check_list"]=self.check_list
  self.results["assert_list"]=self.assert_list
  self.results["screen_info"]=self.screen_info
 def _teardown_log(self):
  logger.removeFilter(self._console_handle)
  logger.removeHandler(self._case_log_handler)
  self._case_log_handler.close()
 def _teardown_result(self):
  filename=self.wrap_filename("{0}.json".format(self._testMethodName))
  self.results["filename"]=os.path.basename(filename)
  f=open(filename,"w")
  json.dump(self.results,f,indent=4)
  f.close()
 def tearDown(self):
  self._teardown_collect()
  self._teardown_collect_other()
  self._teardown_log()
  self._teardown_result()
 def _add_assert_info(self,name,ret,reason=None):
  self.__assert_index+=1
  self.assert_list.append({"name":name,"ret":ret,"msg":reason,"img":self.hook_assert(name,ret,reason),})
 def __getattribute__(self,item):
  attr=super().__getattribute__(item)
  if item.startswith("assert")and callable(attr):
   def _hook_assert(*args,**kwargs):
    called_frame=inspect.getouterframes(inspect.currentframe(),2)
    called_name=called_frame[1][3]
    signature=inspect.signature(attr)
    try:
     msg_index=list(signature.parameters.keys()).index("msg")
    except ValueError:
     msg_index=-1
    ret=True
    print_msg=None
    try:
     attr(*args,**kwargs)
    except AssertionError as e:
     self._has_assert_error=True
     ret=False
     print_msg=str(e)
     raise
    finally:
     if called_name and not called_name.startswith("assert"):
      if msg_index<len(args):
       name=args[msg_index]
      else:
       name=kwargs.get("msg")
      self._add_assert_info(name,ret,print_msg)
   return _hook_assert
  else:
   return attr
 @property
 def screen_dir(self):
  screen_dir=self.wrap_filename("images")
  if not os.path.exists(screen_dir):
   os.makedirs(screen_dir)
  return screen_dir
 def add_screen(self,name,path,url):
  self.screen_info.append({"name":name,"url":url,"path":self.get_relative_path(path),"ts":time.time(),"datetime":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),})
 def wrap_filename(self,filename):
  return os.path.abspath(os.path.join(self.test_config.case_output,filename))
 def get_relative_path(self,path):
  output=self.test_config.case_output
  if not output.endswith(os.path.sep):
   output=output+os.path.sep
  if not os.path.isabs(path):
   path=os.path.abspath(path)
  if not path.startswith(output):
   logger.error("%s not in outputs: %s"%(path,output))
  else:
   path=path[len(output):]
  return path
 def hook_assert(self,name,ret,reason=None):
  pass
# Created by pyminifier (https://github.com/liftoff/pyminifier)
