#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import time
import websocket
import json
from.minium_object import MiniumObject
from uuid import uuid4
import threading
import logging
CLOSE_TIMEOUT=5
MAX_WAIT_TIMEOUT=60
g_thread=None
logger=logging.getLogger()
class DevToolMessage(dict):
 def __getattr__(self,name):
  try:
   return self[name]
  except KeyError:
   raise AttributeError(name)
def json2obj(data):
 return json.loads(data,object_hook=DevToolMessage)
class Connection(MiniumObject):
 def __init__(self,uri):
  super().__init__()
  self.observers={}
  self.uri=uri
  self._is_connected=False
  self._msg_lock=threading.Condition()
  self._ws_event_queue=dict()
  self._req_id_counter=int(time.time()*1000)%10000000000
  self._is_connected=False
  self._sync_wait_msg_id=None
  self._sync_wait_msg=None
  self._method_wait=None
  self._client=websocket.WebSocketApp(self.uri,on_open=self._on_open,on_message=self._on_message,on_error=self._on_error,on_close=self._on_close,)
  self._connect()
 def register(self,method:str,callback):
  if method not in self.observers:
   self.observers[method]=[]
  self.observers[method].append(callback)
 def remove(self,method:str):
  del self.observers[method]
 def notify(self,method:str,message):
  if method not in self.observers:
   return
  for callback in self.observers[method]:
   callback(message)
 def _connect(self,timeout=30):
  self._thread=threading.Thread(target=self._ws_run_forever,args=())
  self._thread.daemon=True
  self._thread.start()
  s=time.time()
  while time.time()-s<timeout:
   if self._is_connected:
    logger.info("connect to WebChatTools successfully")
    break
  else:
   raise Exception("connect to server timeout: %s, thread:%s"%(self.uri,self._thread.is_alive()))
 def _ws_run_forever(self):
  try:
   self._client.run_forever()
  except:
   self.logger.exception("websocket run error")
   return
  self.logger.info("websocket run forerver shutdown")
 def send(self,method,params=None,max_timeout=None):
  if not params:
   params={}
  uid=uuid4()
  message=json.dumps({"id":str(uid),"method":method,"params":params},separators=(',',':'))
  self._client.send(message)
  self._sync_wait_msg_id=str(uid)
  self.logger.debug("SEND > %s"%message)
  return self._receive_response(max_timeout)
 def send_async(self,method,params=None):
  if not params:
   params={}
  uid=uuid4()
  message=json.dumps({"id":str(uid),"method":method,"params":params})
  self._client.send(message)
  self.logger.debug("SEND > %s"%message)
  return uid
 def _receive_response(self,max_timeout=None):
  if max_timeout is None:
   max_timeout=MAX_WAIT_TIMEOUT
  self._msg_lock.acquire()
  self._msg_lock.wait(max_timeout)
  self._msg_lock.release()
  if self._sync_wait_msg_id is None: 
   if "error" in self._sync_wait_msg and "message" in self._sync_wait_msg["error"]:
    err_msg=self._sync_wait_msg["error"]["message"]
    if err_msg:
     raise Exception(err_msg)
   return self._sync_wait_msg
  else:
   record_id=self._sync_wait_msg_id
   self._sync_wait_msg_id=None
   self._sync_wait_msg=None
   raise Exception("receive from remote timeout, id: %s"%record_id)
 def _on_close(self):
  self._is_connected=False
 def _on_open(self):
  self._is_connected=True
 def _on_message(self,message):
  self.logger.debug("RECV < %s"%message)
  ret_json=json2obj(message)
  if ret_json is not None and "id" in ret_json: 
   req_id=ret_json["id"]
   if req_id==self._sync_wait_msg_id:
    self._sync_wait_msg_id=None
    self._sync_wait_msg=ret_json
    self._msg_lock.acquire()
    self._msg_lock.notify()
    self._msg_lock.release()
   else:
    self.logger.error("abandon msg: %s",req_id)
  else: 
   if "method" in ret_json and self._method_wait==ret_json["method"]:
    self._method_wait=None
    self._msg_lock.acquire()
    self._msg_lock.notify()
    self._msg_lock.release()
   if "method" in ret_json and "params" in ret_json:
    self.notify(ret_json["method"],ret_json["params"])
 def _push_event(self,method,params):
  if method in self._ws_event_queue:
   self._ws_event_queue[method].append(params)
  else:
   self._ws_event_queue[method]=[params]
 def _on_error(self,error):
  logger.error(error)
 def destory(self):
  self._client.close()
  self._thread.join(CLOSE_TIMEOUT)
 def wait_for(self,method:str,max_timeout=None):
  self._method_wait=method
  if max_timeout is None:
   max_timeout=MAX_WAIT_TIMEOUT
  self._msg_lock.acquire()
  self._msg_lock.wait(max_timeout)
  self._msg_lock.release()
  if not self._method_wait:
   return True
  else:
   self.logger.error("Can't wait for %s"%method)
   return False
# Created by pyminifier (https://github.com/liftoff/pyminifier)
