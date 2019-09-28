#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import typing
from.element import*
from.minium_object import MiniumObject,timeout
class Page(MiniumObject):
 def __init__(self,page_id,path,query,connection):
  super().__init__()
  self.page_id=page_id
  self.path=path
  self.query=query
  self.connection=connection
 def __repr__(self):
  return "Page(id={0}, path={1}, query={2})".format(self.page_id,self.path,self.query)
 @property
 def data(self):
  return self._send("Page.getData").result.data
 def wait_data_contains(self,*keys_list,max_timeout=10):
  @timeout(max_timeout)
  def f():
   d=self.data
   for keys in keys_list:
    obj=d
    for key in keys:
     if obj and key in obj:
      obj=obj[key]
     else:
      return False
   return True
  try:
   f()
   return True
  except TimeoutError:
   return False
 @data.setter
 def data(self,data):
  self._send("Page.setData",{"data":data})
 def get_element(self,selector,inner_text=None,value=None,text_contains=None,max_timeout=20)->BaseElement:
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
 def call_method(self,method,args=None):
  if not args:
   args=[]
  if isinstance(args,dict):
   args=[args]
  self._send("Page.callMethod",{"method":method,"args":args})
 def get_elements(self,selector,max_timeout=20)->typing.List[BaseElement]:
  return self._get_elements(selector,max_timeout)
 @property
 def inner_size(self):
  size_arr=self._get_window_properties(["innerWidth","innerHeight"])
  return{"width":size_arr[0],"height":size_arr[1]}
 @property
 def scroll_height(self):
  return self._get_window_properties(["document.documentElement.scrollHeight"])
 @property
 def scroll_width(self):
  return self._get_window_properties(["document.documentElement.scrollWidth"])
 @property
 def scroll_x(self):
  return self._get_window_properties(["scrollX"])
 @property
 def scroll_y(self):
  return self._get_window_properties(["scrollY"])
 def _get_window_properties(self,names=None):
  if names is None:
   names=[]
  return self._send("Page.getWindowProperties",{"names":names}).result.properties
 def scroll_to(self,scroll_top,duration=300):
  self.call_wx_method("pageScrollTo",[{"scrollTop":scroll_top,"duration":duration}])
 def _send(self,method,params=None):
  if params is None:
   params={}
  params["pageId"]=self.page_id
  return self.connection.send(method,params)
 def _get_elements(self,selector,max_timeout=20)->typing.List[BaseElement]:
  elements=[]
  @timeout(max_timeout)
  def refresh_elements():
   ret=self._send("Page.getElements",{"selector":selector})
   if hasattr(ret,"error"):
    raise Exception("Element not found with selector: [%s], cause: %s"%(selector,ret.error))
   for e in ret.result.elements:
    element=BaseElement(e.elementId,self.page_id,e.tagName,self.connection)
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
# Created by pyminifier (https://github.com/liftoff/pyminifier)
