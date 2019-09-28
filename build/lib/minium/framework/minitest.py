#!/usr/bin/env python3
import logging
import os.path
import datetime
import time
import logging
import json
import minium
from.assertbase import AssertBase
import minium.native
import minium.wechatdriver.minium_log
logger=logging.getLogger()
is_share_ide=False
g_minium=None
g_native=None
g_log_message_list=[]
def release_minium(cfg):
 global g_minium,g_native
 if not cfg.close_ide and g_minium:
  g_minium.shutdown()
 if cfg.platform!="ide" and not cfg.close_ide:
  g_native.stop_wechat()if g_native else logger.info("Native module has not start, there is no need to stop WeChat")
 if g_native:
  g_native.release()
 g_minium=None
 g_native=None
def get_native(cfg):
 global g_native
 if g_native is None:
  g_native=minium.native.get_native_driver(cfg.platform,cfg.device_desire)
  if cfg.platform!="ide" and not cfg.close_ide:
   mini=get_minium(cfg)
   g_native.start_wechat()
   mini.enable_remote_debug(connect_timeout=cfg.remote_connect_timeout)
 return g_native
def get_minium(cfg):
 global g_minium
 if g_minium is None:
  g_minium=minium.Minium(project_path=cfg.project_path,test_port=cfg.test_port,dev_tool_path=cfg.dev_tool_path)
  if cfg.enable_app_log:
   g_minium.connection.register("App.logAdded",mini_log_added)
   g_minium.app.enable_log()
 return g_minium
def init_minium(cfg):
 get_minium(cfg)
 get_native(cfg)
def mini_log_added(message):
 dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 message["dt"]=dt
 g_log_message_list.append(message)
class MiniTest(AssertBase):
 mini=None
 native=None
 log_message_list=[]
 @classmethod
 def setUpClass(cls):
  super(MiniTest,cls).setUpClass()
  if not cls.CONFIG.report_usage:
   minium.wechatdriver.minium_log.existFlag=1
  cls.mini=get_minium(cls.CONFIG)
  cls.native=get_native(cls.CONFIG)
  cls.app=cls.mini.app
  cls.DEVICE_INFO["system_info"]=cls.mini.get_system_info()
 @classmethod
 def tearDownClass(cls):
  if not is_share_ide:
   release_minium(cls.CONFIG)
 def setUp(self):
  super(MiniTest,self).setUp()
  if self.test_config.auto_relaunch:
   self.app.go_home()
 def tearDown(self):
  global g_log_message_list
  try:
   weapp_path="weapp.log"
   weapp_filename=self.wrap_filename(weapp_path)
   log_messages=g_log_message_list
   g_log_message_list=[]
   with open(weapp_filename,"w")as f:
    for log_message in log_messages:
     f.write(json.dumps(log_message,ensure_ascii=False)+"\n")
   self.results["weapp_log_path"]=weapp_path
   self.capture("teardown")
   self.results["page_data"]=self.page.data
  except:
   self.results["page_data"]=None
  super(MiniTest,self).tearDown()
 @property
 def page(self)->minium.Page:
  return self.mini.app.get_current_page()
 def capture(self,name):
  time.sleep(1)
  filename="%s.%0d.jpg"%(datetime.datetime.now().strftime("%H%M%S"),int(time.time()*1000)%1000,)
  path=os.path.join(self.screen_dir,filename)
  self.native.screen_shot(path)
  if os.path.exists(path):
   self.add_screen(name,path,self.page.path)
  else:
   logger.warning("%s not exists",path)
  return path
 def assertPageData(self,data,msg=None):
  pass
 def assertContainTexts(self,texts,msg=None):
  pass
 def assertTexts(self,texts,selector="",msg=None):
  for text in texts:
   elem=self.page.get_element(selector,inner_text=text)
   if elem is None:
    raise AssertionError(u"selector:%s, inner_text=%s not Found")
 def hook_assert(self,name,ret,reason=None):
  if not self.test_config.no_assert_capture:
   self.capture("{0}-{1}".format(name,"success" if ret else "failed"))
# Created by pyminifier (https://github.com/liftoff/pyminifier)
