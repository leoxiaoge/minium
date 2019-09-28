#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from.minium_object import MiniumObject,timeout
import time
from.prefixer import*
class BaseElement(MiniumObject):
 def __init__(self,element_id,page_id,tag_name,connection):
  super().__init__()
  self.element_id=element_id
  self.page_id=page_id
  self._tag_name=tag_name
  self.connection=connection
 def tap(self):
  self._send("Element.tap")
 def click(self):
  self._send("Element.tap")
  time.sleep(1)
 def long_press(self,duration=350):
  self._touch_start()
  time.sleep(duration/1000)
  self._touch_end()
 def touch_start(self):
  self._touch_start()
 def touch_end(self):
  self._touch_end()
 def touch_move(self):
  self._send("Element.touchmove")
 def touch_cancel(self):
  self._send("Element.touchcancel")
 def slide(self,direction,distance):
  raise NotImplementedError()
 def get_element(self,selector,inner_text=None,value=None,text_contains=None,max_timeout=10):
  @timeout(max_timeout)
  def _f():
   elements=self._get_elements(selector,max_timeout)
   if not elements:
    return True
   for element in elements:
    if inner_text and element.inner_text!=inner_text:
     continue
    if value and element.value()!=value:
     continue
    if text_contains and text_contains not in element.inner_text:
     continue
    return element
   return False
  try:
   r=_f()
   if r is True:
    return None
   else:
    return r
  except:
   return None
 def get_elements(self,selector,max_timeout=10):
  return self._get_elements(selector,max_timeout)
 def attribute(self,name):
  return self._getter("getAttributes","attributes",name)
 @property
 def size(self):
  size_arr=self._dom_property(["offsetWidth","offsetHeight"])
  return{"width":size_arr[0],"height":size_arr[1]}
 def offset(self):
  offset_arr=self._dom_property(["offsetLeft","offsetTop"])
  return{"x":offset_arr[0],"y":offset_arr[1]}
 @property
 def rect(self):
  rect_arr=self._dom_property(["offsetLeft","offsetTop","offsetWidth","offsetHeight"])
  return{"x":rect_arr[0],"y":rect_arr[1],"width":rect_arr[2],"height":rect_arr[3],}
 def styles(self,names):
  return self._getter("getStyles","styles",names)
 @property
 def value(self):
  return self._property("value")[0]
 @property
 def inner_text(self):
  return self._dom_property("innerText")[0]
 @property
 def inner_wxml(self):
  return self._send("Element.getWXML",{"type":"inner"}).result.wxml
 @property
 def outer_wxml(self):
  return self._send("Element.getWXML",{"type":"outer"}).result.wxml
 def _property(self,name):
  return self._getter("getProperties","properties",name)
 def _dom_property(self,name):
  return self._getter("getDOMProperties","properties",name)
 def handle_picker(self,value):
  self._trigger("change",{"value":value})
 def trigger(self,trigger_type,detail):
  return self._trigger(trigger_type,detail)
 def _trigger(self,trigger_type,detail):
  params=dict()
  params["type"]=trigger_type
  if detail:
   params["detail"]=detail
  return self._send("Element.triggerEvent",params)
 def _getter(self,method,return_name,names=""):
  if isinstance(names,list):
   result=self._send("Element."+method,{"names":names})
  elif isinstance(names,str):
   result=self._send("Element."+method,{"names":[names]})
  else:
   raise Exception("invalid names type")
  ret=getattr(result.result,return_name)
  return ret
 def _send(self,method,params=None):
  if params is None:
   params={}
  params["elementId"]=self.element_id
  params["pageId"]=self.page_id
  return self.connection.send(method,params)
 def _touch_start(self):
  self._send("Element.touchstart")
 def _touch_end(self):
  self._send("Element.touchend")
 def _get_elements(self,selector,max_timeout=10):
  elements=[]
  @timeout(max_timeout)
  def refresh_elements():
   ret=self._send("Element.getElements",{"selector":selector})
   if hasattr(ret,"error"):
    raise Exception("Element not found with selector: [%s], cause: %s"%(selector,ret.error))
   for el in ret.result.elements:
    element=BaseElement(el.elementId,self.page_id,el.tagName,self.connection)
    elements.append(element)
   return elements
  try:
   self.logger.info("try to find elements: %s"%selector)
   refresh_elements()
   self.logger.info("find elements success: %s"%str(elements))
   return elements
  except Exception as e:
   self.logger.exception("elements search fail cause: "+str(e))
   return[]
class FormElement(BaseElement):
 def __init__(self):
  super().__init__()
 def set_value(self,value):
  pass
 def get_value(self):
  pass
 def clear(self):
  pass
 def submit(self):
  pass
class MediaElement(BaseElement):
 def __init__(self):
  super().__init__()
  self.controller=MediaController()
  self.media_type=MediaType.UNKNOW
 def get_controller(self):
  return self.controller
 def get_media_type(self):
  return self.media_type
 def get_status(self):
  pass
class VideoElement(BaseElement):
 def __init__(self,element_id,page_id,tag_name,connection):
  super(VideoElement,self).__init__(element_id,page_id,tag_name,connection)
  self.controller=VideoController(connection)
  self.media_type=MediaType.VIDEO
 def play(self):
  self.controller.play()
 def pause(self):
  self.controller.pause()
 def stop(self):
  self.controller.stop()
 def seek(self,position:int):
  self.controller.seek(position)
 def send_danmu(self,text:str,color="#000000"):
  self.controller.send_danmu(text,color)
 def playback_rate(self,rate:float):
  self.controller.playback_rate(rate)
 def request_full_screen(self,direction=0):
  self.controller.request_full_screen(direction)
 def exit_full_screen(self):
  self.controller.exit_full_screen()
 def show_status_bar(self):
  self.controller.show_status_bar()
 def hide_status_bar(self):
  self.controller.hide_status_bar()
class AudioElement(BaseElement):
 def __init__(self,element_id,page_id,tag_name,connection):
  super(AudioElement,self).__init__(element_id,page_id,tag_name,connection)
  self.controller=AudioController(connection)
  self.media_type=MediaType.AUDIO
 def set_src(self,src):
  self.controller.set_src(src)
 def play(self):
  self.controller.play()
 def pause(self):
  self.controller.pause()
 def seek(self,position):
  self.controller.seek(position)
class LivePlayerElement(BaseElement):
 def __init__(self,element_id,page_id,tag_name,connection):
  super(LivePlayerElement,self).__init__(element_id,page_id,tag_name,connection)
  self.controller=LivePlayerController(connection)
  self.media_type=MediaType.LIVE_PLAY
 def play(self):
  self.controller.play()
 def stop(self):
  self.controller.stop()
 def mute(self):
  self.controller.mute()
 def pause(self):
  self.controller.pause()
 def resume(self):
  self.controller.resume()
 def request_full_screen(self,direction=0):
  self.controller.request_full_screen(direction)
 def exit_full_screen(self):
  self.controller.exit_full_screen()
 def snapshot(self):
  self.controller.snapshot()
class LivePusherElement(BaseElement):
 def __init__(self,element_id,page_id,tag_name,connection):
  super(LivePusherElement,self).__init__(element_id,page_id,tag_name,connection)
  self.controller=LivePusherController(connection)
  self.media_type=MediaType.LIVE_PUSH
 def start(self):
  self.controller.start()
 def stop(self):
  self.controller.stop()
 def pause(self):
  self.controller.pause()
 def resume(self):
  self.controller.resume()
 def switch_camera(self):
  self.controller.switch_camera()
 def snapshot(self):
  self.controller.snapshot()
 def toggle_torch(self):
  self.controller.toggle_torch()
 def play_bgm(self,url):
  self.controller.play_bgm(url)
 def stop_bgm(self):
  self.controller.stop_bgm()
 def pause_bgm(self):
  self.controller.pause_bgm()
 def resume_bgm(self):
  self.controller.resume_bgm()
 def set_bgm_volume(self,volume):
  self.controller.set_bgm_volume(volume)
 def start_preview(self):
  self.controller.start_preview()
 def stop_preview(self):
  self.controller.stop_preview()
class MediaController(MiniumObject):
 def __init__(self):
  pass
class VideoController(MediaController):
 def __init__(self,connection):
  super().__init__()
  self.connection=connection
 def play(self):
  self.evaluate("function(){global.minium.videoContext.play()}")
 def pause(self):
  self.evaluate("function(){global.minium.videoContext.pause()}")
 def stop(self):
  self.evaluate("function(){global.minium.videoContext.stop()}")
 def seek(self,position:int):
  self.evaluate("function(){global.minium.videoContext.seek(%s)}"%position)
 def send_danmu(self,text:str,color="#000000"):
  self.evaluate("function(){global.minium.videoContext.sendDanmu({text:'%s', color:'%s'})}"%(text,color))
 def playback_rate(self,rate):
  self.evaluate("function(){global.minium.videoContext.playbackRate(%s)}"%rate)
 def request_full_screen(self,direction=0):
  self.evaluate("function(){global.minium.videoContext.requestFullScreen({direction: %s})}"%direction)
 def exit_full_screen(self):
  self.evaluate("function(){global.minium.videoContext.exitFullScreen()}")
 def show_status_bar(self):
  self.evaluate("function(){global.minium.videoContext.showStatusBar()}")
 def hide_status_bar(self):
  self.evaluate("function(){global.minium.videoContext.hideStatusBar()}")
class AudioController(MediaController):
 def __init__(self,connection):
  super().__init__()
  self.connection=connection
 def set_src(self,src):
  self.evaluate("function(){global.minium.audioContext.setSrc(%s)}"%src)
 def play(self):
  self.evaluate("function(){global.minium.audioContext.play()}")
 def pause(self):
  self.evaluate("function(){global.minium.audioContext.pause()}")
 def seek(self,position):
  self.evaluate("function(){global.minium.audioContext.seek(%s)}"%position)
class LivePlayerController(MediaController):
 def __init__(self,connection):
  super().__init__()
  self.connection=connection
 def play(self):
  self.evaluate("function(){global.minium.livePlayerContext.play()}")
 def stop(self):
  self.evaluate("function(){global.minium.livePlayerContext.stop()}")
 def mute(self):
  self.evaluate("function(){global.minium.livePlayerContext.mute()}")
 def pause(self):
  self.evaluate("function(){global.minium.livePlayerContext.pause()}")
 def resume(self):
  self.evaluate("function(){global.minium.livePlayerContext.resume()}")
 def request_full_screen(self,direction=0):
  self.evaluate("function(){global.minium.livePlayerContext.requestFullScreen({direction: %s})}"%direction)
 def exit_full_screen(self):
  self.evaluate("function(){global.minium.livePlayerContext.exitFullScreen()}")
 def snapshot(self):
  self.evaluate("function(){global.minium.livePlayerContext.snapshot()}")
class LivePusherController(MediaController):
 def __init__(self,connection):
  super().__init__()
  self.connection=connection
 def start(self):
  self.evaluate("function(){global.minium.livePusherContext.start()}")
 def stop(self):
  self.evaluate("function(){global.minium.livePusherContext.stop()}")
 def pause(self):
  self.evaluate("function(){global.minium.livePusherContext.pause()}")
 def resume(self):
  self.evaluate("function(){global.minium.livePusherContext.resume()}")
 def switch_camera(self):
  self.evaluate("function(){global.minium.livePusherContext.switchCamera()}")
 def snapshot(self):
  self.evaluate("function(){global.minium.livePusherContext.snapshot()}")
 def toggle_torch(self):
  self.evaluate("function(){global.minium.livePusherContext.toggleTorch()}")
 def play_bgm(self,url):
  self.evaluate("function(){global.minium.livePusherContext.PlayBGM({url:'%s'})}"%url)
 def stop_bgm(self):
  self.evaluate("function(){global.minium.livePusherContext.stopBGM()}")
 def pause_bgm(self):
  self.evaluate("function(){global.minium.livePusherContext.pauseBGM()}")
 def resume_bgm(self):
  self.evaluate("function(){global.minium.livePusherContext.resumeBGM()}")
 def set_bgm_volume(self,volume):
  self.evaluate("function(){global.minium.livePusherContext.setBGMVolume({volume:'%s'})}"%volume)
 def start_preview(self):
  self.evaluate("function(){global.minium.livePusherContext.startPreview()}")
 def stop_preview(self):
  self.evaluate("function(){global.minium.livePusherContext.startPreview()}")
# Created by pyminifier (https://github.com/liftoff/pyminifier)
