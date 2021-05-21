import json, os, sys

templatepath=sys.argv[1]
with open(templatepath+"/inputoption.json",'r') as f:
   optionfile = json.loads(f.read())

finalinput={}
for k,v in optionfile.items():
    ip={k:v["value"]}
    finalinput.update(ip)

ipjson=json.dumps(finalinput)
with open(templatepath+"/input.json",'w') as f:
    inputfile = f.write(ipjson)

parameters=[]
for k,v in finalinput.items():
    parameter={
        "ParameterKey": k,
        "ParameterValue": v
    }
    parameters.append(parameter)

prams=json.dumps(parameters)

with open(templatepath+"/parameters.json",'w') as f:
   inputfile = f.write(prams)