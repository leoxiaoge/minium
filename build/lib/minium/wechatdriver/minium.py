#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import platform
import os
import base64
import json
import logging
from.error import*
from.app import App
from.connection import Connection
from.minium_object import MiniumObject
LOG_FORMATTER="%(levelname)-5.5s %(asctime)s %(filename)-10s %(funcName)-15s %(lineno)-3d %(message)s"
MAC_DEVTOOL_PATH="/Applications/wechatwebdevtools.app/Contents/MacOS/cli"
WINDOWS_DEVTOOL_PATH="cli"
TEST_PORT=9420
UPLOAD_URL="https://stream.weixin.qq.com/weapp/UploadFile"
cur_path=os.path.dirname(os.path.realpath(__file__)) 
resource_path=os.path.join(os.path.dirname(cur_path),"resources")
if not os.path.exists(resource_path):
 os.mkdir(resource_path) 
class LogLevel(object):
 INFO=20
 DEBUG_SEND=12
 METHOD_TRACE=11
 DEBUG=9
def build_version():
 config_path=os.path.join(os.path.dirname(__file__),"version.json")
 if not os.path.exists(config_path):
  return{}
 else:
  with open(config_path,"rb")as f:
   version=json.load(f)
   return version
class Minium(MiniumObject):
 app:App
 def __init__(self,uri="ws://localhost",dev_tool_path="",project_path=None,test_port=None,show_log=False,):
  super().__init__()
  if show_log:
   console_handler=logging.StreamHandler()
   formatter=logging.Formatter(LOG_FORMATTER)
   console_handler.setFormatter(formatter)
   self.logger.addHandler(console_handler)
   self.logger.setLevel(logging.DEBUG)
  self.version=build_version()
  self.logger.info(self.version)
  if not test_port:
   test_port=TEST_PORT
  test_port=str(test_port)
  self.sessions={}
  self.app=None
  self.connection=None
  self.uri=uri+":"+test_port
  self.project_path=project_path
  self.test_port=test_port
  self.is_remote=False
  if not dev_tool_path=="":
   self.dev_tool_path=dev_tool_path
  elif "Darwin" in platform.platform():
   self.dev_tool_path=MAC_DEVTOOL_PATH
  elif "Windows" in platform.platform():
   self.dev_tool_path=WINDOWS_DEVTOOL_PATH
  else:
   self.logger.warning("Dev tool doesn't support current OS yet")
  self._is_windows="Windows" in platform.platform()
  self.launch_dev_tool()
 def _dev_cli(self,cmd):
  if not self.dev_tool_path or not os.path.exists(self.dev_tool_path):
   raise MiniumEnvError("dev_tool_path: %s not exists"%self.dev_tool_path)
  if self._is_windows:
   cmd_template='"%s"  %s'
  else:
   cmd_template="%s %s"
  return self._do_shell(cmd_template%(self.dev_tool_path,cmd))
 def launch_dev_tool(self):
  self.logger.info("Starting dev tool ...")
  if self.project_path:
   if not os.path.exists(self.project_path):
    raise MiniumEnvError("project_path: %s not exists"%self.project_path)
   if not os.path.isdir(self.project_path):
    raise MiniumEnvError("project_path: %s is not director"%self.project_path)
   start_cmd="--auto %s --auto-port %s"%(self.project_path,self.test_port)
   status=self._dev_cli(start_cmd)
   if self._is_windows:
    time.sleep(10)
   else:
    time.sleep(5)
   if status[-1]=="" or "Port %s is in use"%self.test_port in status[-1]:
    self.logger.info("Dev tool is opening, but can't open project, quit now...")
    self._dev_cli("--quit")
    time.sleep(3)
    self.logger.info("Starting dev tool again...")
    status=self._dev_cli(start_cmd)
    if status[-1]=="":
     raise Exception("Please check MiniProgram project if config error or not")
    else:
     self.logger.info("Restart finish")
  else:
   status=["Open project with automation enabled success  /Users/sherlock/svn/demo"]
  if "Open project with automation enabled success " in status[-1]:
   try:
    connection=Connection(self.uri)
    self.app=App(connection)
    self.connection=connection
   except Exception as e:
    import traceback
    traceback.print_exc()
    self.logger.exception(str(e))
    exit(0)
  else:
   self.logger.warning( """Open project with automation enabled fail! Please try to open project :
                %s -o %s"""   % (self.dev_tool_path, self.project_path)
   )
 def launch_dev_tool_with_login(self):
  cmd_start="-l --login-qr-output terminal --auto --auto %s --auto-port %s"%(self.project_path,self.test_port,)
  status=self._dev_cli(cmd_start)
  if "Open project with automation enabled success " in status[-1]:
   connection=Connection(self.uri)
   self.app=App(connection)
   self.connection=connection
  else:
   self.logger.error("Open project with automation enabled fail! make sure project path is right")
   exit(-1)
 def get_app_json(self):
  if not self.project_path:
   return None
  try:
   paths=[os.path.join(self.project_path,"app.json"),os.path.join(self.project_path,"miniprogram","app.json"),]
   for path in paths:
    if os.path.exists(path):
     return json.load(open(path,"rb"))
   raise FileNotFoundError()
  except Exception as e:
   self.logger.error("Get app json fail, cause: %s"%str(e))
   return None
 def get_system_info(self):
  return self.app.call_wx_method("getSystemInfoSync").result.result
 def enable_remote_debug(self,use_push=True,path=None,connect_timeout=None):
  if connect_timeout is None:
   connect_timeout=180
  if use_push:
   self.connection.send("Tool.enableRemoteDebug",params={"auto":True})
   self.is_remote=True
   self.connection.wait_for(method="App.initialized")
   return
  if path is None:
   path=os.path.join(resource_path,"debug_qrcode.jpg")
  qr_data=self.connection.send("Tool.enableRemoteDebug",max_timeout=connect_timeout).result.qrCode
  with open(path,"wb")as qr_img:
   qr_img.write(base64.b64decode(qr_data))
  return path
 def shutdown(self):
  if self.is_remote:
   self.logger.info("MiniProgram closing")
   self.app.exit()
  self.logger.info("Dev tool closing")
  if self.project_path:
   status=self._dev_cli("--quit")
   if status and "quit IDE success" in status[-1]:
    self.logger.info("Dev tool has quit, Minium Test complete")
   else:
    self.logger.warning("Minium Test complete, but dev tool has not quit yet")
if __name__=="__main__":
 mini=Minium(project_path="/Users/sherlock/svn/demo")
 mini.connection.register("App.logAdded",mini.hello)
 mini.app.enable_log()
 system_info=mini.get_system_info()
 page=mini.app.get_current_page()
 page2=mini.app.switch_tab("/page/tabBar/API/index")
# Created by pyminifier (https://github.com/liftoff/pyminifier)
