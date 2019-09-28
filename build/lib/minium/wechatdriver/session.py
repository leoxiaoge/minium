#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from.app import App
from uuid import uuid4
class Session(object):
 def __init__(self,app_name,session_name):
  self.id=uuid4()
  self.app_name=app_name
  self.name=session_name
 def connect(self):
  pass
 def disconnect(self):
  pass
 def set_options(self,options):
  self.options=options
 def health_check(self):
  pass
 def open_app(self):
  self.app=App(self.options.uuid)
  pass
 def close_app(self):
  pass
 def reopen_app(self):
  pass
# Created by pyminifier (https://github.com/liftoff/pyminifier)
