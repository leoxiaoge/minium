#!/usr/bin/env python3
import os.path
import sys
work_root=os.path.abspath(os.path.dirname(__file__))
lib_path=os.path.join(work_root,"lib")
sys.path.insert(0,lib_path)
from minium.native.minative.androidnative import AndroidNative
from minium.native.minative.iosnative import IOSNative
from minium.native.minative.idenative import IdeNative
OS_ANDROID="android"
OS_IOS="ios"
OS_IDE="ide"
def get_native_driver(os_name,conf):
 if os_name.lower()==OS_ANDROID:
  return AndroidNative(conf)
 elif os_name.lower()==OS_IOS:
  return IOSNative(conf)
 elif os_name.lower()==OS_IDE:
  return IdeNative(conf)
 else:
  raise RuntimeError("runtime")
# Created by pyminifier (https://github.com/liftoff/pyminifier)
