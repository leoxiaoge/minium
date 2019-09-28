#!/usr/bin/env python3
from.basenative import BaseNative,NativeError
class IdeNative(BaseNative):
 def release(self):
  pass
 def start_wechat(self):
  pass
 def stop_wechat(self):
  pass
 def connect_weapp(self,path):
  pass
 def screen_shot(self,filename,return_format="raw"):
  pass
 def pick_media_file(self,cap_type="camera",media_type="photo",original=False,duration=5.0,names=None,):
  pass
 def input_text(self,text):
  pass
 def input_clear(self):
  pass
 def textarea_text(self,text,index=1):
  pass
 def textarea_clear(self,index=0):
  pass
 def allow_login(self):
  pass
 def allow_get_user_info(self,answer=True):
  pass
 def allow_get_location(self,answer=True):
  pass
 def handle_modal(self,title=None,answer="确定"):
  pass
 def handle_action_sheet(self,item):
  pass
 def forward_miniprogram(self,names:list,text:str=None,create_new_chat:bool=True):
  pass
 def forward_miniprogram_inside(self,names:list,create_new_chat:bool=True):
  pass
 def send_custom_message(self,message=None):
  pass
 def phone_call(self):
  pass
 def map_select_location(self,name):
  pass
 def map_back_to_mp(self):
  pass
 def deactivate(self,duration):
  pass
 def get_authorize_settings(self):
  pass
 def back_from_authorize_setting(self):
  pass
 def authorize_page_checkbox_enable(self,name,enable):
  pass
# Created by pyminifier (https://github.com/liftoff/pyminifier)
