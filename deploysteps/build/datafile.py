import os,sys,time,logging,json,random,math
from datetime import datetime
import json,os,sys,shutil
from shutil import copyfile

def load_txt_file(filepath):
	path=filepath
	if os.path.exists(path):
		file_object=open(path,"r")
		datastring=file_object.read()
		successmessage=filepath+" loaded Successfully"
		return("success", successmessage, datastring)
	else:
		errormessage=filepath+" not found"
		Error="file does not exist"
		return("error", errormessage, str(Error))

def load_code_file(sourcepath,destinationpath):
	try:
		srcpath=sourcepath
		destpath=destinationpath
		directory = os.path.dirname(destpath)
		if not os.path.exists(directory):
			os.makedirs(directory)
		copyfile(srcpath, destpath)
		successmessage=destinationpath+" created Successfully"
		return('success',successmessage,destinationpath)
	except OSError as e:
		errormessage=destinationpath+"CREATION_FAILED"
		return("error",errormessage,str(e))

def load_s3_file(filepath):
	path=filepath
	if os.path.exists(path):
		file_object=open(path,"r")
		datastring=file_object.read()
		data=json.loads(datastring)
		successmessage=filepath+" loaded Successfully"
		return("success", successmessage, data)
	else:
		errormessage=filepath+" not found"
		Error="file does not exist"
		return("error", errormessage, str(Error))