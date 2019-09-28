#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler 
import colorlog 
import time
import datetime
import os
import types
import json
import requests
import queue
import threading
logger=logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
def process_report():
 global existFlag
 while not existFlag:
  lock.acquire()
  lock.wait(10)
  lock.release()
  if not report_queue.empty():
   data=report_queue.get()
   report(data=data)
def report(data:dict):
 try:
  ret=requests.post(url="https://minitest.weixin.qq.com/xbeacon/user_report/api_log",data=json.dumps(data),timeout=10)
  if not ret.status_code==200:
   global fail,existFlag
   fail+=1
   if fail>=10:
    existFlag=1
  else:
   fail=0
 except Exception as e:
  try:
   ret=requests.post(url="http://minitest.weixin.qq.com/xbeacon/user_report/api_log",data=json.dumps(data),timeout=10)
   if not ret.status_code==200:
    fail+=1
    if fail>=10:
     existFlag=1
   else:
    fail=0
  except Exception as e:
   pass
existFlag=0
fail=0
lock=threading.Condition()
report_queue=queue.Queue()
thread=threading.Thread(target=process_report)
thread.setDaemon(True)
thread.start()
usage=[]
app_id=None
version=None
revision=None
def minium_log(func):
 @wraps(func)
 def wrapper(*args,**kwargs):
  global usage,app_id,version,revision
  start=datetime.datetime.now()
  result=func(*args,**kwargs)
  end=datetime.datetime.now()
  new_args=[args[0].__dict__]+list(args[1:])
  if(version is None or revision is None)and hasattr(args[0],"version"):
   version=args[0].version["version"]
   revision=args[0].version["revision"]
  if app_id is None and hasattr(args[0],"app_id"):
   app_id=args[0].app_id
  if app_id is None:
   usage.append({"version":version,"revision":revision,"app_id":app_id,"func":func.__name__,"args":str(new_args),"kwargs":kwargs,"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"consuming":int((end-start).total_seconds()*1000),})
  else:
   report_queue.put({"version":version,"revision":revision,"app_id":app_id,"func":func.__name__,"args":str(new_args),"kwargs":kwargs,"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"consuming":int((end-start).total_seconds()*1000),})
   for f in usage:
    f["app_id"]=app_id
    report_queue.put(f)
   lock.acquire()
   lock.notify()
   lock.release()
  return result
 return wrapper
class MonitorMetaClass(type):
 def __new__(mcs,cls_name,bases,attr_dict):
  for k,v in attr_dict.items():
   if(isinstance(v,types.FunctionType)and not k.startswith("_")and not k.startswith("send")and not k.startswith("register")and not k.startswith("notify")and not k.startswith("remove")):
    attr_dict[k]=minium_log(v)
  return type.__new__(mcs,cls_name,bases,attr_dict)
def singleton(cls):
 _instance={}
 @wraps(cls)
 def inner(*args,**kwargs):
  if cls not in _instance:
   _instance[cls]=cls(*args,**kwargs)
  return _instance[cls]
 return inner
log_colors_config={"DEBUG":"cyan","INFO":"green","WARNING":"yellow","ERROR":"red","CRITICAL":"red","DEBUG_SEND":"white","METHOD_TRACE":"blue","APP_LOG":"green","NATIVE":"purple",}
APP_LOG=21
DEBUG_SEND=13
METHOD_TRACE=12
NATIVE=11
logging.addLevelName(APP_LOG,"APP_LOG")
logging.addLevelName(DEBUG_SEND,"DEBUG_SEND")
logging.addLevelName(METHOD_TRACE,"METHOD_TRACE")
@singleton
class Log(object):
 def __init__(self,logName=None):
  self.logName=logName
  self.logger=logging.getLogger()
  self.formatter=colorlog.ColoredFormatter("%(log_color)s[%(asctime)s] [%(filename)s: %(lineno)d] [%(levelname)s]: %(message)s",log_colors=log_colors_config,) 
  self.info=self.logger.info
  self.debug=self.logger.debug
  self.error=self.logger.error
  self.exception=self.logger.exception
  self.warning=self.logger.warning
 def app_log(self,message,*args,**kws):
  if self.logger.isEnabledFor(APP_LOG):
   self.logger._log(APP_LOG,message,args,**kws)
 def debug_send(self,message,*args,**kws):
  if self.logger.isEnabledFor(DEBUG_SEND):
   self.logger._log(DEBUG_SEND,message,args,**kws)
 def method_trace(self,message,*args,**kws):
  if self.logger.isEnabledFor(METHOD_TRACE):
   self.logger._log(METHOD_TRACE,message,args,**kws)
 def native_log(self,message,*args,**kws):
  if self.logger.isEnabledFor(NATIVE):
   self.logger._log(NATIVE,message,args,**kws)
 def get_file_sorted(self,file_path):
  dir_list=os.listdir(file_path)
  if not dir_list:
   return
  else:
   dir_list=sorted(dir_list,key=lambda x:os.path.getmtime(os.path.join(file_path,x)))
   return dir_list
 def TimeStampToTime(self,timestamp):
  timeStruct=time.localtime(timestamp)
  return str(time.strftime("%Y-%m-%d",timeStruct))
 def handle_logs(self):
  dir_list=["logs"] 
  for dir in dir_list:
   dirPath=(os.path.abspath(os.path.dirname(os.path.dirname(__file__)))+"/"+dir) 
   file_list=self.get_file_sorted(dirPath) 
   if file_list: 
    for i in file_list:
     file_path=os.path.join(dirPath,i) 
     t_list=self.TimeStampToTime(os.path.getctime(file_path)).split("-")
     now_list=self.TimeStampToTime(time.time()).split("-")
     t=datetime.datetime(int(t_list[0]),int(t_list[1]),int(t_list[2])) 
     now=datetime.datetime(int(now_list[0]),int(now_list[1]),int(now_list[2]))
     if(now-t).days>6: 
      self.delete_logs(file_path)
    if len(file_list)>4: 
     file_list=file_list[0:-4]
     for i in file_list:
      file_path=os.path.join(dirPath,i)
      print(file_path)
      self.delete_logs(file_path)
 def delete_logs(self,file_path):
  try:
   os.remove(file_path)
  except PermissionError as e:
   Log().warning("删除日志文件失败：{}".format(e))
 def create_handle(self):
  if self.logName is None:
   return
  self.fh=RotatingFileHandler(filename=self.logName,mode="a",maxBytes=1024*1024*5,backupCount=5,encoding="utf-8",) 
  self.fh.setLevel(logging.DEBUG)
  self.fh.setFormatter(self.formatter)
  self.logger.addHandler(self.fh)
  self.ch=colorlog.StreamHandler()
  self.ch.setLevel(logging.DEBUG)
  self.ch.setFormatter(self.formatter)
  self.logger.addHandler(self.ch)
 def destory(self):
  pass
if __name__=="__main__":
 log=Log()
 log.debug("---测试开始----")
 log.info("操作步骤")
 log.warning("----测试结束----")
 log.error("----测试错误----")
# Created by pyminifier (https://github.com/liftoff/pyminifier)
