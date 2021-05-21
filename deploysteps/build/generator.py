import os,sys,time,logging,json,random,math
from datetime import datetime
import json,os,sys,shutil
from shutil import copyfile

import datafile
import generatebuildcode

templatepath = sys.argv[1]
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

def generate_codedata():
    status,statusmessage,load_api_config = datafile.load_s3_file(apifilepath)
    if status == "error":
        message={"statusCode":400,"errorMessage":"load_requirement error","Error":load_api_config}
        return(message)
    for version in load_api_config["versions"]:
        versionid = version["versionid"]
        for resourceid in version["resources"]:
            resourcefilepath = datapath+"/servicedesigns/"+serviceid+"/api/"+versionid+"/resources/"+resourceid+"/config.json"
            blueprints = []
            import_module_app = []
            requirement_txt = []
            status,statusmessage,load_resource_config = datafile.load_s3_file(resourcefilepath)
            if status == "error":
                message={"statusCode":400,"errorMessage":"load_requirement error","Error":load_resource_config}
                return(message)
            for method in load_resource_config["methods"]:
                methodid = method["Ref"]
                methodpath=datapath+"/servicedesigns/"+serviceid+"/api/"+versionid+"/resources/"+resourceid+"/methods/"+methodid
                methodcodepath=methodpath+"/code/"+methodid+".py"
                methodrequirementpath=methodpath+"/code/requirement.txt"
                localcodepath="codepath/"+serviceid+"/"+resourceid+"/code/"+methodid+".py"
                
                copystatus,copystatusmessage,copycode=datafile.load_code_file(methodcodepath,localcodepath)
                if copystatus == "error":
                    message={"statusCode":400,"errorMessage":"copycode error","Error":copycode}
                    return(message)
                
                status,statusmessage,load_requirement = datafile.load_txt_file(methodrequirementpath)
                if status == "error":
                    message={"statusCode":400,"errorMessage":"load_requirement error","Error":load_requirement}
                    return(message)
                
                requirement_txt.append(load_requirement)
                import_blueprint_form = 'from '+methodid+' import '+methodid
                import_module_app.append(import_blueprint_form)
                blueprint_form = "app.register_blueprint("+methodid+")"
                blueprints.append(blueprint_form)
                requirement_filepath= "codepath/"+serviceid+"/"+resourceid+"/code/requirement.txt"
            
                requirement_status,requirement_statusmessage,requirement_file = generatebuildcode.generate_requirement_file(serviceid,resourceid,requirement_txt,requirement_filepath)
                if requirement_status == "error":
                    message={"statusCode":400,"errorMessage":"requirement_file error","Error":requirement_file}
                    return(message)
                
                appcode_path = "codepath/"+serviceid+"/"+resourceid+"/code/app.py"
                app_py_status,app_py_statusmessage,app_py = generatebuildcode.generate_app_python_file(serviceid,resourceid,blueprints,import_module_app,appcode_path)
                if app_py_status == "error":
                    message={"statusCode":400,"errorMessage":"app_py error","Error":app_py}
                    return(message)
                
                dokerfilepath= "codepath/"+serviceid+"/"+resourceid+"/Dockerfile"
                docker_status,docker_statusmessage,docker_file_create = generatebuildcode.generate_docker_file(serviceid,resourceid,dokerfilepath)
                if docker_status == "error":
                    message={"statusCode":400,"errormessage":"docker_file_create error","Error":docker_file_create}
                    return(message)

def create_inputjson():
    with open(templatepath+"/inputoption.json",'r') as f:
        optionfile = json.loads(f.read())

    finalinput={}
    for k,v in optionfile.items():
        ip={k:v["value"]}
        finalinput.update(ip)
    
    resources = getresourceids()
    finalinput.update({"resources": resources})
    finalinput.update({"serviceid": serviceid})

    prams=json.dumps(finalinput)
    with open(templatepath+"/input.json",'w') as f:
        inputfile = f.write(prams)

generate_codedata()
create_inputjson()