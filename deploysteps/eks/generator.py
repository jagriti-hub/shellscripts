import os,sys,time,logging,json,random,math
from datetime import datetime
import json,os,sys,shutil,yaml

templatepath= sys.argv[1]
serviceid = sys.argv[2]

def create_inputjson():
    with open(templatepath+"/inputoption.json",'r') as f:
        optionfile = json.loads(f.read())

    finalinput={}
    for k,v in optionfile.items():
        ip={k:v["value"]}
        finalinput.update(ip)
    finalinput.update({"serviceid": serviceid})

    prams=json.dumps(finalinput)
    with open(templatepath+"/input.json",'w') as f:
        inputfile = f.write(prams)

create_inputjson()