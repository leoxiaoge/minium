#!/usr/bin/env python3
import sys
import inspect
import os.path
import re
from.import minitest
target_base_class=minitest.MiniTest
def parse_document(doc_str):
 pair={}
 if not doc_str:
  return pair
 for line in doc_str.split("\n"):
  m=re.search(r"@(\w+)[\s:](.*)",line)
  if m:
   pair[m.group(1).lower()]=m.group(2)
 return pair
def import_module(module_name):
 module_name=module_name.strip()
 comps=module_name.split(".")
 mod=__import__(module_name)
 if len(comps)<2:
  return mod
 else:
  for name in comps[1:]:
   mod=getattr(mod,name)
 return mod
def doc_format(doc_str):
 if doc_str is None:
  return None
 old_lines=doc_str.split("\n")
 min_space_count=0
 for line in old_lines:
  line=line.replace("\t","    ")
  space_count=0
  for a in line:
   if a==" ":
    space_count+=1
   else:
    break
  if min_space_count<space_count:
   min_space_count=space_count
  if len(line)<min_space_count:
   min_space_count=len(line)
 new_lines=[line[min_space_count:]for line in old_lines]
 try:
  return u"\n".join(new_lines).strip()
 except:
  return doc_str
def get_test_methods(test_case_class):
 s=[]
 for name,value in inspect.getmembers(test_case_class):
  if name.startswith("test"):
   if callable(getattr(test_case_class,name)):
    for attr_name,func_obj in inspect.getmembers(value):
     if attr_name=="__code__":
      pair=parse_document(value.__doc__)
      s.append({"human_case_name":pair.get("name"),"name":name,"start":func_obj.co_firstlineno,"filename":func_obj.co_filename,"doc":doc_format(value.__doc__),"co_names":func_obj.co_names,})
 return s
def load_module(path):
 sys.path+=path
 test_cases={}
 human_name_mapping={}
 for root,dirs,filenames in os.walk(path):
  for filename in filenames:
   if not filename.endswith(".py"):
    continue
   module_path=os.path.join(root,filename)
   has_hit_names=set()
   mod_memebers={}
   module_path=os.path.relpath(os.path.abspath(module_path),os.path.abspath(path))
   module_name=".".join(module_path.replace(os.path.sep,".").split(".")[:-1])
   mod=import_module(module_name)
   human_name=getattr(mod,"NAME",None)
   human_id=getattr(mod,"ID",0)
   if human_name:
    if module_name.endswith(".__init__"):
     module_name=module_name[:-1*len(".__init__")]
    human_name_mapping[module_name]={"human_case_module":human_name,"module_id":human_id,}
   for memname,memobj in inspect.getmembers(mod):
    if inspect.isclass(memobj)and issubclass(memobj,target_base_class):
     mod_memebers[memname]=memobj
   for memname,memobj in mod_memebers.items():
    leaf_obj=memobj
    for other_name,other_obj in mod_memebers.items(): 
     if issubclass(other_obj,memobj)and other_obj is not leaf_obj:
      has_hit_names.add(leaf_obj)
      leaf_obj=other_obj
    if leaf_obj not in has_hit_names:
     has_hit_names.add(leaf_obj)
     case_list=get_test_methods(leaf_obj)
     if case_list:
      test_cases[module_name]={"case_list":case_list,"human_case_module":human_name,"module_id":human_id,}
 for module_name,module_info in test_cases.items():
  module_sp=module_name.split(".")
  human_info={}
  for i in range(len(module_sp)):
   m=".".join(module_sp[:len(module_sp)-i])
   if m in human_name_mapping:
    human_info=human_name_mapping[m]
  module_info.update(human_info)
 return test_cases
def find_test_class(module_name,test_name):
 for cls in get_test_classes(module_name):
  if test_name in dir(cls):
   return cls
def get_test_classes(module_name):
 classes=[]
 test_module=import_module(module_name)
 for name in dir(test_module):
  obj=getattr(test_module,name)
  if isinstance(obj,type):
   if issubclass(obj,minitest.AssertBase):
    classes.append(obj)
 return classes
# Created by pyminifier (https://github.com/liftoff/pyminifier)
