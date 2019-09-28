#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
from.minium_log import MonitorMetaClass
import subprocess
from functools import wraps
import time
import logging
logger=logging.getLogger()
def timeout(duration):
 def spin_until_true(func):
  @wraps(func)
  def wrapper(*args,**kwargs):
   timeout=time.time()+duration
   r=func(*args,**kwargs)
   while not r:
    time.sleep(1)
    if timeout<time.time():
     raise TimeoutError("timeout for %s"%func.__name__)
    r=func(*args,**kwargs)
   return r
  return wrapper
 return spin_until_true
class MiniumObject(object,metaclass=MonitorMetaClass):
 def __init__(self):
  self.logger=logger
  self.observers={}
  self.connection=None
 def _do_shell(self,command,print_msg=True):
  self.logger.info("de shell: %s"%command)
  p=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  lines=[]
  for line in iter(p.stdout.readline,b""):
   try:
    line=line.rstrip().decode("utf8")
   except UnicodeDecodeError:
    line=line.rstrip().decode("gbk")
   logger.debug(line)
   lines.append(line)
  return lines
 def call_wx_method(self,method,args=None):
  return self._call_wx_method(method=method,args=args)
 def mock_wx_method(self,method,result):
  self._mock_wx_method(method=method,result=result)
 def restore_wx_method(self,method):
  self.connection.send("App.mockWxMethod",{"method":method})
 def evaluate(self,app_function:str,args=None):
  self._evaluate(app_function=app_function,args=args)
 def _call_wx_method(self,method,args=None):
  if args is None:
   args=[]
  if isinstance(args,dict):
   args=[args]
  params={"method":method,"args":args}
  return self.connection.send("App.callWxMethod",params)
 def _evaluate(self,app_function:str,args=None):
  if not args:
   args=[]
  return self.connection.send_async("App.callFunction",{"functionDeclaration":app_function,"args":args})
 def _mock_wx_method(self,method,result):
  self.connection.send("App.mockWxMethod",{"method":method,"result":result})
# Created by pyminifier (https://github.com/liftoff/pyminifier)
