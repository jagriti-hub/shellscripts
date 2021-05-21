import os,sys,time,logging,json,random,math
from datetime import datetime

import datafile

def generate_app_python_file(serviceid,resourceid, blueprint_import,import_blueprint_form,appcode_path):
    print("Generating app.py for Flask")
    # appcode_path = archeplaydatapath+"/deploy/published/"+serviceid+"/"+resourceid+"/code"
    import_module = 'from flask import Flask\n'
    import_blueprint = import_blueprint_form
    flask_initialise = "app = Flask(__name__)"
    add_blueprint = blueprint_import
    main_func = 'if __name__ == \"__main__\":\n    app.run()'

    try:
      app_py = open(appcode_path, "w")
      app_py.write(import_module + "\n"+"\n".join(import_blueprint)+"\n\n" + flask_initialise + "\n\n" + "\n".join(add_blueprint) + "\n\n" + main_func + "\n\n")
      app_py.close()
      successmessage = appcode_path+" created Successfully"
      return("success",successmessage,appcode_path)
    except Exception as Error:
      return("error","Python_WSGI_Codefile_Write_error",Error)

def generate_docker_file(serviceid,resourceid,dokerfilepath):
    print("Generating Dockerfile for deployment")
    try:
        # dokerfilepath= archeplaydatapath+"/deploy/published/"+serviceid+"/"+resourceid+"/"+"Dockerfile"
        dockerfilef = open(dokerfilepath, "w")
        dockerfilef.write('FROM python:3.8.1-slim-buster\nRUN addgroup --system app && adduser --system --ingroup app app\nENV APP_HOME=/home/app/web\nRUN mkdir $APP_HOME\nWORKDIR $APP_HOME\nADD code $APP_HOME\nRUN pip install --upgrade pip -r requirement.txt\nRUN chown -R app:app $APP_HOME\nUSER app\nCMD [\"gunicorn\", \"--bind\", \"0.0.0.0:5000\", \"app:app\"]')
        dockerfilef.close()
        successmessage = dokerfilepath+" created Successfully"
        return("success",successmessage,dokerfilepath)
    except Exception as Error:
        return("error","Dockerfile_Write_error",Error)

def generate_requirement_file(serviceid,resourceid,requirement_data,requirement_filepath):
    print("Generating requirement for deployment")
    try:
        # requirement_filepath= archeplaydatapath+"/deploy/published/"+serviceid+"/"+resourceid+"/code/"+"requirement.txt"
        requirementf = open(requirement_filepath, "w")
        requirementf.write("\n".join(requirement_data))
        requirementf.close()
        successmessage = requirement_filepath+" created Successfully"
        return("success",successmessage,requirement_filepath)
    except Exception as Error:
        return("error","Dockerfile_Write_error",Error)