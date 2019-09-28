#!/usr/bin/env python3
import json
import os.path
import sys
import glob
import shutil
def generate_meta(outputs):
 filenames=glob.glob(os.path.join(outputs,"*","*","test_*.json"))
 case_datas=[]
 for filename in filenames:
  relative_path=os.path.sep.join(filename.split(os.path.sep)[-3:-1])
  m=json.load(open(filename,"rb"))
  m["relative"]=relative_path
  case_datas.append(m)
 summary={"case_num":len(case_datas),"success":len([c for c in case_datas if c["success"]]),"failed":len([c for c in case_datas if c["is_failure"]]),"error":len([c for c in case_datas if c["is_error"]]),"costs":"",}
 case_datas.sort(key=lambda a:a["start_timestamp"])
 meta_json={"case_datas":case_datas,"summary":summary}
 return meta_json
def imp_main(input_path,output_path=None):
 if output_path is None:
  output_path=input_path
 if os.path.exists(output_path)and input_path!=output_path:
  print("delete ",output_path)
  shutil.rmtree(output_path)
 if input_path!=output_path:
  shutil.copytree(input_path,output_path)
 meta_json=generate_meta(output_path)
 json.dump(meta_json,open(os.path.join(output_path,"meta.json"),"w"),indent=4)
 dist_path=os.path.join(os.path.dirname(__file__),"dist")
 for filename in os.listdir(dist_path):
  path=os.path.join(dist_path,filename)
  target=os.path.join(output_path,filename)
  if os.path.exists(target):
   if os.path.isdir(target):
    shutil.rmtree(target)
   else:
    os.remove(target)
  if os.path.isdir(path):
   shutil.copytree(path,target)
  else:
   shutil.copy(path,target)
def main():
 if len(sys.argv)<2 or sys.argv[1]=="-h":
  print( """
Usage: minireport data_path report_output_path\n data_path: default report data folder is the folder named 'output' in case folder\n report_output_path: wherever you want            """  
  )
  exit(0)
 input_path=sys.argv[1]
 output_path=None
 if len(sys.argv)>2:
  output_path=sys.argv[2]
 return imp_main(input_path,output_path)
if __name__=="__main__":
 main()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
