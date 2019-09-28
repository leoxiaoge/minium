#!/usr/bin/env python3
import os.path
import at
from.basenative import BaseNative,NativeError
WECHAT_PACKAGE="com.tencent.mm"
WECHAT_ACTIVITY="ui.LauncherUI"
class UiDefine:
 def __init__(self,_at:at.At):
  self.at=_at
  self.btn_authorize_ok=self.at.e.cls_name("android.widget.Button").text("允许")
  self.btn_authorize_cancel=self.at.e.cls_name("android.widget.Button").text("取消")
  self.action_menu=self.at.e.cls_name("android.widget.ImageButton").desc("更多")
  self.action_home=self.at.e.cls_name("android.widget.ImageButton").desc("关闭")
  self.title=(self.action_home.parent().cls_name("android.widget.LinearLayout").instance(1).child().cls_name("android.widget.TextView"))
  self.comp_picker_input=self.at.e.cls_name("android.widget.EditText").rid("android:id/numberpicker_input")
class AndroidNative(BaseNative):
 def connect_weapp(self,path):
  self.at.apkapi.launch()
  gallery_name="atstub"
  self.at.apkapi.add_gallery(path)
  self.stop_wechat()
  self.start_wechat()
  self.e.text("发现").click()
  self.e.text("扫一扫").click()
  self.e.cls_name("android.widget.ImageButton").click()
  self.e.text("从相册选取二维码").click()
  self.e.text("所有图片").click()
  self.e.text(gallery_name).click()
  self.e.desc_contains("图片 1").click()
  self.e.text_contains("扫描中").wait_disappear()
 def screen_shot(self,filename,quality=30):
  return self.at.device.screen_shot(filename,quality=quality)
 def pick_media_file(self,cap_type="camera",media_type="photo",original=False,duration=5.0,index_list=None,):
  pass
 def input_text(self,text):
  pass
 def _allow_authorize(self,answer):
  if answer:
   self.ui.btn_authorize_ok.click()
  else:
   self.ui.btn_authorize_cancel.click()
 def allow_login(self,answer=True):
  self._allow_authorize(answer)
 def allow_get_user_info(self,answer=True):
  self._allow_authorize(answer)
 def allow_get_location(self,answer=True):
  pass
 def handle_modal(self,btn_text="确定",title=None):
  if title:
   self.e.text(title).parent().cls_name("android.widget.FrameLayout").child().cls_name("android.widget.Button").text(btn_text).click()
  self.e.cls_name("android.widget.Button").text(btn_text).click()
 def handle_action_sheet(self,item):
  self.e.cls_name("android.widget.TextView").text(item).click()
 def forward_miniprogram(self,name,text=None,create_new_chat=True):
  self.ui.action_menu.click()
  self.e.text("转发").click()
  return self.forward_miniprogram_inside(name,text,create_new_chat)
 def forward_miniprogram_inside(self,name,text=None,create_new_chat=True):
  if create_new_chat:
   self.e.text("创建新聊天").click()
   self.e.text_contains(name).click(True)
   self.e.text("确定(1)").enabled(True).click()
  else:
   self.e.text_contains(name).click(True)
  if text:
   self.e.edit_text().enter(text)
  self.e.cls_name("android.widget.Button").text("发送").click()
  self.e.text("已转发").wait_disappear()
 def send_custom_message(self,message=None):
  pass
 def call_phone(self):
  pass
 def handle_picker(self,*items):
  instance=0
  for item in items:
   input_elem=self.ui.comp_picker_input.instance(instance)
   next_elem=input_elem.parent().child("android.widget.Button")
   first_text=input_elem.get_text()
   while True:
    current_text=input_elem.get_text()
    if current_text==str(item):
     break
    if first_text==str(item):
     raise NativeError(f" not found")
   instance+=1
 def __init__(self,json_conf):
  super(AndroidNative,self).__init__(json_conf)
  if json_conf is None:
   json_conf={}
  self.serial=json_conf.get("serial")
  uiautomator_version=int(json_conf.get("uiautomator_version","2"))
  at.uiautomator_version=uiautomator_version
  self.at=at.At(self.serial)
  self.ui=UiDefine(self.at)
 def get_authorize_settings(self):
  ui_views=self.at.java_driver.dump_ui()
  setting_map={}
  for ui_view in ui_views:
   if ui_view.cls_name=="android.view.View" and ui_view.content_desc in["已开启","已关闭",]:
    check_status=True if ui_view.content_desc=="已开启" else False
    parant_view=ui_view.sibling().get_children()[0]
    setting_map[parant_view.text]=check_status
  return setting_map
 def back_from_authorize_setting(self):
  self.at.adb.press_back()
 def authorize_page_checkbox_enable(self,name,enable):
  setting_map=self.get_authorize_settings()
  if setting_map.get(name)==enable:
   return
  self.e.text(name).parent().instance(2).child().cls_name("android.view.View").click()
  if not enable:
   self.e.cls_name("android.widget.Button").text("关闭授权").click_if_exists(5)
 def release(self):
  self.at.release()
 def start_wechat(self):
  self.at.adb.start_app(WECHAT_PACKAGE,WECHAT_ACTIVITY)
 def stop_wechat(self):
  self.at.adb.stop_app(WECHAT_PACKAGE)
 @property
 def e(self):
  return self.at.e
# Created by pyminifier (https://github.com/liftoff/pyminifier)
