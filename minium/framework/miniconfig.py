#!/usr/bin/env python3
import os.path
import json
import logging
import yaml
logger=logging.getLogger()
default_config={"platform":"ide","debug_mode":"info","close_ide":False,"no_assert_capture":False,"auto_relaunch":False,"device_desire":{},"report_usage":True,"remote_connect_timeout":180}
def get_log_level(debug_mode):
 return{"info":logging.INFO,"debug":logging.DEBUG,"warn":logging.WARNING,"error":logging.ERROR,}.get(debug_mode,logging.INFO)
class MiniConfig(dict):
 def __init__(self,from_dict=None):
  for k,v in default_config.items():
   setattr(self,k,v)
  if from_dict is None:
   self.is_default_config=True
  else:
   self.is_default_config=False
   for k,v in from_dict.items():
    setattr(self,k,v)
  super(MiniConfig,self).__init__(self.__dict__)
 def __getattr__(self,item):
  try:
   return self[item]
  except KeyError:
   return None
 def __setattr__(self,key,value):
  self[key]=value
 @classmethod
 def from_file(cls,filename):
  logger.info("load config from %s",filename)
  _,ext=os.path.splitext(filename)
  f=open(filename,"rb")
  if ext==".json":
   json_dict=json.load(f)
  elif ext==".yml" or ext==".yaml":
   json_dict=yaml.load(f)
  else:
   raise RuntimeError(f"unknown extension {ext} for {filename}")
  f.close()
  return MiniConfig(json_dict)
if __name__=="__main__":
 a=MiniConfig({"outputs":"xxxx"})
 print(a.outputs)
 print(a.sss)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
