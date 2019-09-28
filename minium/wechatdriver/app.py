#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from.page import Page
from.element import*
from.minium_object import MiniumObject,timeout
import os
import threading
cur_path=os.path.dirname(os.path.realpath(__file__)) 
conf_path=os.path.join(os.path.dirname(cur_path),"conf/iOS_conf")
class App(MiniumObject):
 def __init__(self,connection):
  super().__init__()
  self.connection=connection
  self._create_context_listener()
  self._route_change_listener()
  self._msg_lock=threading.Condition()
  self.route_is_changed=False
  self.main_page_path="/"+self._get_launch_options_sync().result.result.path
  self.current_path_path=self.main_page_path
  self.current_page_id=self._current_page().page_id
  self.app_id=self._get_account_info_sync().result.result.miniProgram.appId
  self.current_video_id=None
  self.video_this=None
  self.current_audio_id=None
  self.audio_this=None
  self.current_live_player_id=None
  self.live_player_this=None
 def enable_log(self):
  self.connection.send("App.enableLog")
 def exit(self):
  self.connection.send("App.exit")
 def get_account_info_sync(self):
  return self._get_account_info_sync()
 def expose_function(self,name,binding_function):
  self._expose_function(name,binding_function)
 def get_current_page(self)->Page:
  return self._current_page()
 def _current_page(self):
  ret=self.connection.send("App.getCurrentPage")
  if hasattr(ret,"error"):
   raise Exception("Get current page fail, cause: %s"%ret.error)
  page=Page(ret.result.pageId,"/"+ret.result.path,ret.result.query,self.connection)
  self.current_path_path=page.path
  self.current_page_id=page.page_id
  return page
 def get_page_stack(self):
  ret=self.connection.send("App.getPageStack")
  page_stack=[]
  for page in ret.result.pageStack:
   page_stack.append(Page(page.pageId,page.path,page.query,self.connection))
  return page_stack
 def go_home(self):
  page=(self._relaunch(self.main_page_path)if self.main_page_path!="/" else self._relaunch("/"+self._get_launch_options_sync().result.result.path))
  return page
 def _get_launch_options_sync(self):
  return self._call_wx_method("getLaunchOptionsSync")
 def _change_route(self,open_type,path,is_wait_url_change=True):
  self._call_wx_method(open_type,[{"url":path}])
  if self._route_changed():
   return self._current_page()
  else:
   return self._current_page()
 def _on_route_changed(self,message):
  if not message.name=="onAppRouteDone":
   return
  self.route_is_changed=True
  self.current_path_path=message.args[0].path
  self.current_page_id=message.args[0].webviewId
  self._msg_lock.acquire()
  self._msg_lock.notify()
  self._msg_lock.release()
  self.logger.info("Route changed, %s"%message)
 def _on_video_context_created(self,message):
  if not message.name=="onVideoContextCreated":
   return
  self.logger.info(message)
  self.current_video_id=message.args[0]
  self.video_this=message.args[1]
 def _on_audio_context_created(self,message):
  if not message.name=="onAudioContextCreated":
   return
  self.logger.info(message)
  self.current_audio_id=message.args[0]
  self.audio_this=message.args[1]
 def _on_live_pusher_context_created(self,message):
  if not message.name=="onLivePusherContextCreated":
   return
  self.logger.info(message)
 def _on_live_player_context_created(self,message):
  if not message.name=="onLivePlayerContextCreated":
   return
  self.logger.info(message)
  self.current_live_player_id=message.args[0]
  self.live_player_this=message.args[1]
 def video_context(self):
  return VideoElement(self._current_page().get_element("video").element_id,self.current_page_id,"video",self.connection)
 def audio_context(self):
  return AudioElement(self._current_page().get_element("audio").element_id,self.current_page_id,"audio",self.connection)
 def live_pusher_context(self):
  return LivePusherElement(self._current_page().get_element("live-pusher").element_id,self.current_page_id,"live-pusher",self.connection)
 def live_player_context(self):
  return LivePlayerElement(self._current_page().get_element("live-player").element_id,self.current_page_id,"live-player",self.connection)
 def navigate_to(self,url,params=None,is_wait_url_change=True):
  if params:
   url+="?"+"&".join(["%s=%s"%(k,v)for k,v in params.items()])
  self.logger.info("NavigateTo: %s"%url)
  page=self._change_route("navigateTo",url,is_wait_url_change)
  if page.path!=url:
   self.logger.warning("NavigateTo(%s) fail ! Current page has not change"%url)
  return page
 def redirect_to(self,url):
  wait=False if url==self._current_page()else True
  self.logger.info("RedirectTo: %s"%url)
  page=self._change_route("redirectTo",url,wait)
  if page.path!=url:
   self.logger.warning("RedirectTo(%s) fail ! Current page has not change"%url)
  return page
 def relaunch(self,url):
  return self._relaunch(url=url)
 def navigate_back(self,delta=1):
  self._wait_until_page_is_stable()
  page=self._current_page()
  page_stack=self._page_stack()
  if page.page_id==page_stack[0].page_id:
   self.logger.warning("Current page is root, can't navigate back")
   return page
  self.logger.info("NavigateBack from:%s"%page.path)
  self._call_wx_method("navigateBack",[{"delta":delta}])
  if self._route_changed():
   return self._current_page()
  else:
   self.logger.warning("route has not change, may be navigate back fail")
 def switch_tab(self,url):
  page=self._change_route("switchTab",url)
  if page.path!=url:
   self.logger.warning("Switch tab(%s) fail ! Current page has not change"%url)
  return page
 def mock_show_modal(self,answer=True):
  self._mock_wx_method("showModal",{"cancel":answer,"confirm":False if answer else True,"errMsg":"showModal:ok",},)
 def mock_get_location(self,acc=65,horizontal_acc=65,vertical_acc=65,speed=-1,altitude=0,latitude=23.12908,longitude=113.26436,):
  self._mock_wx_method("getLocation",{"accuracy":acc,"altitude":altitude,"errMsg":"getLocation:ok","horizontalAccuracy":horizontal_acc,"verticalAccuracy":vertical_acc,"latitude":latitude,"longitude":longitude,"speed":speed,},)
 def mock_show_action_sheet(self,tap_index=0):
  self._mock_wx_method("showActionSheet",{"errMsg":"showActionSheet:ok","tapIndex":tap_index})
 @timeout(10)
 def _wait_until_page_is_stable(self):
  return True if self.current_page_id==self._current_page().page_id else False
 @timeout(10)
 def _wait_until_page_is_change(self):
  return True if self.current_page_id!=self._current_page().page_id else False
 def _route_changed(self,timeout=None):
  if not timeout:
   timeout=5
  self._msg_lock.acquire()
  self._msg_lock.wait(timeout)
  self._msg_lock.release()
  if self.route_is_changed:
   self.route_is_changed=False
   return True
  else:
   self.route_is_changed=False
   return False
 def _create_context_listener(self):
  self._expose_function("onVideoContextCreated",self._on_video_context_created)
  self._expose_function("onAudioContextCreated",self._on_audio_context_created)
  self._expose_function("onLivePusherContextCreated",self._on_live_pusher_context_created)
  self._expose_function("onLivePlayerContextCreated",self._on_live_player_context_created)
  self._evaluate( """function () {
 global.minium = {}; var cvc = wx.createVideoContext; Object.defineProperty(wx, "createVideoContext", { get() { return function (videoId, pageOptions) { onVideoContextCreated(videoId, pageOptions); global.minium.videoContext = null; videoContext = cvc(videoId, pageOptions); global.minium.videoContext = videoContext; return videoContext } } }); var cac = wx.createAudioContext; Object.defineProperty(wx, "createAudioContext", { get() { return function (audioId, pageOptions) { onAudioContextCreated(audioId, pageOptions); global.minium.audioContext = null; audioContext = cac(audioId, pageOptions); global.minium.audioContext = audioContext; return audioContext } } }); var clpuc = wx.createLivePusherContext; Object.defineProperty(wx, "createLivePusherContext", { get() { return function () { onLivePusherContextCreated(); global.minium.livePusherContext = null; livePusherContext = clpuc(); global.minium.livePusherContext = livePusherContext; return livePusherContext } } }); var clplc = wx.createLivePlayerContext; Object.defineProperty(wx, "createLivePlayerContext", { get() { return function (playerId, pageOptions) { onLivePlayerContextCreated(playerId, pageOptions); global.minium.livePlayerContext = null; livePlayerContext = clplc(playerId, pageOptions); global.minium.livePlayerContext = livePlayerContext; return livePlayerContext } } });}"""  
  )
 def _route_change_listener(self):
  self._expose_function("onAppRouteDone",self._on_route_changed)
  self._evaluate( """function () {
 wx.onAppRouteDone(function (options) { onAppRouteDone(options) })}"""  
  )
 def _expose_function(self,name,binding_function):
  self.connection.register("App.bindingCalled",binding_function)
  self.connection.send("App.addBinding",{"name":name})
 def _get_account_info_sync(self):
  return self._call_wx_method("getAccountInfoSync")
 def _relaunch(self,url):
  self.logger.info("ReLaunch: %s"%url)
  page=self._change_route("reLaunch",url)
  if page.path!=url:
   self.logger.warning("ReLaunch(%s) fail ! Current page has not change"%url)
  time.sleep(1)
  return page
 def _page_stack(self):
  ret=self.connection.send("App.getPageStack")
  page_stack=[]
  for page in ret.result.pageStack:
   page_stack.append(Page(page.pageId,page.path,page.query,self.connection))
  return page_stack
# Created by pyminifier (https://github.com/liftoff/pyminifier)
