import os,sys,time,logging,json,random,math
from datetime import datetime
import json,os,sys,shutil,yaml
from shutil import copyfile

import datafile

templatepath= sys.argv[1]
serviceid = sys.argv[2]
datapath = "/home/app/web/archeplay/data"
apifilepath = datapath+"/servicedesigns/"+serviceid+"/api/config.json"

def getresourceids():
    resources=[]
    status,statusmessage,load_api_config = datafile.load_s3_file(apifilepath)
    if status == "error":
        message={"statusCode":400,"errorMessage":"load_requirement error","Error":load_api_config}
        return(message)
    for version in load_api_config["versions"]:
        versionid = version["versionid"]
        for resourceid in version["resources"]:
            resources.append(resourceid)
    return(resources)

def create_inputjson():
    with open(templatepath+"/inputoption.json",'r') as f:
        optionfile = json.loads(f.read())
    finalinput={}
    for k,v in optionfile.items():
        ip={k:v["value"]}
        finalinput.update(ip)

    status,statusmessage,load_api_config = datafile.load_s3_file(apifilepath)
    if status == "error":
        message={"statusCode":400,"errorMessage":"load_requirement error","Error":load_api_config}
        return(message)
    for version in load_api_config["versions"]:
        versionid = version["versionid"]
        versionname = version["versionname"]
        for resourceid in version["resources"]:
            resourcefilepath = datapath+"/servicedesigns/"+serviceid+"/api/"+versionid+"/resources/"+resourceid+"/config.json"
            
            status,statusmessage,load_resource_config = datafile.load_s3_file(resourcefilepath)
            if status == "error":
                message={"statusCode":400,"errorMessage":"load_requirement error","Error":load_resource_config}
                return(message)
            
            if os.path.isdir(templatepath+"/"+resourceid) == False:
                os.mkdir(templatepath+"/"+resourceid)
            
            finalinput.update({"resourceid": resourceid})
            finalinput.update({"serviceid": serviceid})
            resourcename = load_resource_config["resourcename"]
            generateatt = {
                "DeployName": "deloy"+resourceid, #form deploy_resourceid
                "HpaName": "hpa"+resourceid, #form hpa_resourceid
                "IngressName": "ingress"+resourceid, #form
                "LabelName": resourceid, #form
                "NameSpace": "default", #form
                "Protocol": "TCP", #form
                "ServiceName": "service"+resourceid, #form
                "ImageName": resourceid, #form
                "Containername": resourceid, #form
                "Resourceurl": "/"+versionname+"/"+resourcename+"/$2", #form
                "ResourceEndpoint": "/"+versionname+"/"+resourcename+"(/|$)(.*)", #form
                "Cpu": "250m",
                "memory": "500Mi"
            }
            finalinput.update(generateatt)
            prams=json.dumps(finalinput)
            with open(templatepath+"/"+resourceid+"/input.json",'w') as f:
                inputfile = f.write(prams)


def create_valuesyaml():
    resourceids = getresourceids()
    resources = {"resources": resourceids}
    res=json.dumps(resources)
    with open(templatepath+"/resinput.json",'w') as f:
        resip = f.write(res)
    
    for resourceid in resourceids:
        with open(templatepath+"/"+resourceid+"/input.json",'r') as f:
            inputjson = json.loads(f.read())
        ipjsonstr = json.dumps(inputjson)
        with open(templatepath+"/"+resourceid+"/values.yaml",'w') as f:
            yamlfile = yaml.dump((f.write(ipjsonstr)))

create_inputjson()
create_valuesyaml()