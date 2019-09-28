#!/usr/bin/env python3
import requests
from.basenative import BaseNative,NativeError
from wx_wda import*
class IOSNative(BaseNative):
 def __init__(self,json_conf):
  super(IOSNative,self).__init__(json_conf)
  self.udid=json_conf.get("device_info").get("udid")
  self.wda_project_path=json_conf.get("wda_project_path")
  self.wda_runner=WebDriverRunner(self.udid,self.wda_project_path)
  self.app=None
 def start_wechat(self):
  device=DeviceTool(self.udid)
  device.find_app(bundle_id="com.tencent.xin")
  for i in range(3):
   try:
    logger.info("第 %d 次启动微信, 共3次机会"%(i+1))
    self.app=WdaUI(server_url="http://localhost:%s"%self.wda_runner.port,bundle_id="com.tencent.xin",)
    self.app.session.set_alert_callback(self._alert_callback)if callable(self._alert_callback)else logger.error("Alert callback would not callable")
    logger.info("微信启动成功")
    return
   except Exception as e:
    logger.error("setup error: 第 %d 次启动微信失败: %s"%((i+1),str(e)))
    logger.info("正在重启 WebDriverAgent ...")
    self.wda_runner.start_driver()
 def connect_weapp(self,path):
  filename="remote_debug.jpg"
  r=requests.post("https://stream.weixin.qq.com/weapp/UploadFile",files={filename:(filename,open(path,"rb"))})
  if r.status_code!=200:
   logger.error(r.text)
   r.raise_for_status()
  url="https://stream.weixin.qq.com/weapp/GetQRCodePage?file_name={0}".format(filename)
  self.start_wechat()
  self.app.session(className="Button",name="通讯录").get(timeout=10.0).click()
  self.app.session(className="SearchField",name="搜索").get(timeout=10.0).set_text("文件传输助手")
  rect=self.app.session(className="Image",name="fts_brand_contact_mask.png").bounds
  self.app.session.click(rect.x,rect.y)
  self.app.session(className="TextView").set_text(url+"\n")
  self.app.session(className="Other",nameContains=url)[-1].get(timeout=10.0).click()
  self.app.session(className="Other",name="小程序web view测试").child(className="Other").child(className="Image").tap_hold(3.0)
  self.app.session(className="Button",name="识别图中二维码").get(timeout=10.0).click()
 def screen_shot(self,filename:str,return_format:str="raw")->object:
  return self.app.client.screenshot(png_filename=filename,format=return_format)
 def pick_media_file(self,cap_type="camera",media_type="photo",original=False,duration=5.0,names=None,):
  if cap_type=="album" and names is None:
   raise Exception("从相册选择照片必须提供照片名称, 可以通过 wda inspector 查看照片名称")
  if cap_type=="camera":
   self._capture_photo(media_type=media_type,duration=duration)
  elif cap_type=="album":
   if media_type=="photo":
    if isinstance(names,str):
     names=[names]
    self._select_photos_from_album(names=names,original=original)
   elif media_type=="video":
    if isinstance(names,list):
     names=names[0]
    self._select_video_from_album(name=names)
 def input_text(self,text):
  self.app.session(className="TextField").set_text(text)
 def input_clear(self):
  self.app.session(className="TextField").clear_text()
 def textarea_text(self,text:str,index=1):
  self.app.session(className="TextView")[index].set_text(text)
 def textarea_clear(self,index=0):
  self.app.session(className="textView")[index].clear_text()
 def allow_login(self,answer=True):
  if answer:
   self.app.session(className="Button",name="Allow").get(timeout=10.0).click()
  else:
   pass
 def allow_get_user_info(self,answer=True):
  if self.app.session(className="StaticText",nameContains="获取你的昵称").exists:
   self.app.session(className="Button",name="允许").get(timeout=10.0).click()if answer else self.app.session(className="Button",name="取消").get(timeout=10.0).click()
 def allow_get_location(self,answer=True):
  if self.app.session(className="StaticText",name="获取你的位置信息").exists:
   self.app.session(className="Button",name="允许").get(timeout=10.0).click()if answer else self.app.session(className="Button",name="拒绝").get(timeout=10.0).click()
 def handle_modal(self,btn_text="确定",title:str=None):
  if title:
   assert self.app.session(nameContains=title).exists,"没有出现预期弹窗: %s"%title
  self.app.session(className="Button",name=btn_text).get(timeout=10.0).click()
 def handle_action_sheet(self,item):
  self.app.session(className="ScrollView").child(className="Button",name=item).get(timeout=10.0).click()
 def forward_miniprogram(self,names,text:str=None,create_new_chat=True):
  self.app.session(className="Button",name="更多").get(timeout=10.0).click()
  self.app.session(className="Button",name="转发").get(timeout=10.0).click()
  self.app.session(className="StaticText",name="创建新的聊天").get(timeout=10.0).click()
  if isinstance(names,str):
   names=[names]
  for name in names:
   self.app.session(className="TextField",name="搜索").get(timeout=10.0).set_text(name)
   self.app.session(className="StaticText",name=name,visible=True).get(timeout=10.0).click()
  self.app.session(className="Button",nameContains="完成").get(timeout=10.0).click()
  self.app.session(className="Button",name="发送").get(timeout=10.0).click()
 def forward_miniprogram_inside(self,names,create_new_chat=True):
  self.app.session(className="StaticText",name="创建新的聊天").get(timeout=10.0).click()
  if isinstance(names,str):
   names=[names]
  for name in names:
   self.app.session(className="TextField",name="搜索").get(timeout=10.0).set_text(name)
   self.app.session(className="StaticText",name=name,visible=True).get(timeout=10.0).click()
  self.app.session(className="Button",nameContains="完成").get(timeout=10.0).click()
  self.app.session(className="Button",name="发送").get(timeout=10.0).click()
 def send_custom_message(self,message:str=None):
  self.app.session(className="TextView").set_text(message+"\n")
 def phone_call(self):
  self.app.session(className="Button",name="呼叫").get(timeout=10.0).click()
  self.app.session.alert.accept()
 def map_select_location(self,name:str):
  self.app.session(className="SearchField",name="搜索地点").get(timeout=10.0).set_text(name)
  self.app.session(name=name,className="StaticText").get(timeout=10.0).click()
  while self.app.session(name=name,className="StaticText").exists:
   try:
    self.app.session(name=name,className="StaticText").get(timeout=10.0).click()
    if self.app.session(className="Button",name="确定").exists:
     break
   except Exception as e:
    logger.warning(str(e))
  self.app.session(className="Button",name="确定").get(timeout=10.0).click()
 def map_back_to_mp(self):
  self.app.session(className="Button",name="返回").get(timeout=10.0).click()
 def deactivate(self,duration):
  self.app.session.deactivate(duration=duration)
 @property
 def orientation(self):
  return self.app.session.orientation()
 @orientation.setter
 def orientation(self,value):
  self.app.session.orientation(value)
 def release(self):
  self.wda_runner.remove_iproxy()
 def _capture_photo(self,media_type,duration=10.0):
  if media_type=="photo":
   self.app.session(text="拍照").get(timeout=10.0).click()
   self.app.session(name="PhotoCapture").get(timeout=10.0).click()
  elif media_type=="video":
   self.app.session(text="拍摄").get(timeout=10.0).click()
   self.app.session(name="VideoCapture").get(timeout=10.0).click()
   time.sleep(duration)
   self.app.session(name="VideoCapture").get(timeout=10.0).click()
  time.sleep(2.0)
  while self.app.session(nameContains="Use ").exists:
   try:
    self.app.session(nameContains="Use ").get(timeout=10.0).click()
   except Exception as e:
    logger.warning(str(e))
 def _select_photos_from_album(self,names:list,original=False):
  self.app.session(text="从手机相册选择").get(timeout=10.0).click()
  for name in names:
   rect=self.app.session(nameContains=name).bounds
   self.app.session.click(rect.x+rect.width-10,rect.y+10)
  if original:
   self.app.session(text="原图发送").get(timeout=10.0).click()
  self.app.session(text="完成").get(timeout=10.0).click()
  self.app.session(text="原图发送").wait_gone(timeout=10.0)
 def _select_video_from_album(self,name:str):
  self.app.session(text="从手机相册选择").get(timeout=10.0).click()
  rect=self.app.session(text="发送").get(timeout=10.0).bounds
  self.app.session(nameContains=name).get(timeout=10.0).click()
  self.app.session(text="取消").wait_gone(timeout=10.0)
  self.app.session.click(rect.x+10,rect.y+10)
  self.app.session(text="发送").wait_gone(timeout=300.0)
 def stop_wechat(self):
  pass
 def get_authorize_settings(self):
  pass
 def back_from_authorize_setting(self):
  self.app.session(className="Button",name="返回").get(timeout=10.0).click()
 def authorize_page_checkbox_enable(self,name,enable):
  pass
 @staticmethod
 def _alert_callback(session):
  logger.info("出现弹框, 默认接受")
  session.alert.accept()
if __name__=="__main__":
 with open("/Users/sherlock/git/minium/native-client/conf/iOS_conf")as json_file:
  import json
  conf=json.load(json_file)
  nv=IOSNative(conf)
  nv.connect_weapp("https://stream.weixin.qq.com/weapp/GetQRCodePage?file_name=remote_debug.jpg")
# Created by pyminifier (https://github.com/liftoff/pyminifier)
