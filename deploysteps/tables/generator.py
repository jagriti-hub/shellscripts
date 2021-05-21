import sys,os,time,math,random
import logging,json

path=sys.argv[1]
serviceid=sys.argv[2]
 
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

def create_input(tableconf):
    tableindexes = tableconf["indexes"]
    paramstructure={}
    paramstructure["TableName"]=tableconf["tablename"]
    AttributeDefinitions=[]
    for attschema in tableconf["schema"]:
        AttributeDefinition = {
            "AttributeName": attschema["attributename"],
            "AttributeType": attschema["attributetype"]
        }
        AttributeDefinitions.append(AttributeDefinition)
    paramstructure["AttributeDefinitions"]=AttributeDefinitions
    primarykeyschema = []
    primarykey = {
        "AttributeName": tableindexes["primary"]["key"],
        "KeyType": "HASH"
    }
    primarykeyschema.append(primarykey)
    if "sortkey" in tableindexes["primary"] and tableindexes["primary"]['sortkey']!="":
        sortkey = {
            "AttributeName": tableindexes["primary"]["sortkey"],
            "KeyType": "RANGE"
        }
        primarykeyschema.append(sortkey)
    paramstructure["KeySchema"]=primarykeyschema
    if tableindexes["primary"]["infra"]["ondemand"] == True:
        paramstructure["BillingMode"]="PAY_PER_REQUEST"
        paramstructure["ProvisionedThroughput"]={
            "ReadCapacityUnits": 0,
            "WriteCapacityUnits": 0
        }
    elif tableindexes["primary"]["infra"]["ondemand"] == False:
        paramstructure["BillingMode"]="PROVISIONED"
        paramstructure["ProvisionedThroughput"]={
            "ReadCapacityUnits": tableindexes["primary"]["infra"]["iops"]["read"],
            "WriteCapacityUnits": tableindexes["primary"]["infra"]["iops"]["write"]
        }
    GlobalSecInd=[]
    if "secondary" in tableindexes:
        secondkeyschema = {}
        keyschema = []
        for secondarykey in tableindexes["secondary"]:
            if "key" in secondarykey:
                secondkey = {
                    "AttributeName": secondarykey["key"],
                    "KeyType": "HASH"
                }
                keyschema.append(secondkey)
            if "sortkey" in  secondarykey and secondarykey["sortkey"] != "":
                secondsortkey = {
                    "AttributeName": secondarykey["sortkey"],
                    "KeyType": "RANGE"
                }
                keyschema.append(secondsortkey)
            secondkeyschema["KeySchema"]=keyschema
            secondkeyschema["IndexName"]=secondarykey["indexname"]
            if secondarykey["infra"]["ondemand"] == True and tableindexes["primary"]["infra"]["ondemand"] == True:
                secondkeyschema["ProvisionedThroughput"]={
                    "ReadCapacityUnits": 0,
                    "WriteCapacityUnits": 0
                }
            elif secondarykey["infra"]["ondemand"] == False and tableindexes["primary"]["infra"]["ondemand"] == True:
                secondkeyschema["ProvisionedThroughput"]={
                    "ReadCapacityUnits": 0,
                    "WriteCapacityUnits": 0
                }
            elif secondarykey["infra"]["ondemand"] == False and tableindexes["primary"]["infra"]["ondemand"] == False:
                secondkeyschema["ProvisionedThroughput"]={
                    "ReadCapacityUnits": secondarykey["infra"]["iops"]["read"],
                    "WriteCapacityUnits": secondarykey["infra"]["iops"]["write"]
                }
            elif secondarykey["infra"]["ondemand"] == True and tableindexes["primary"]["infra"]["ondemand"] == False:
                secondkeyschema["ProvisionedThroughput"]={
                    "ReadCapacityUnits": tableindexes["primary"]["infra"]["iops"]["read"],
                    "WriteCapacityUnits": tableindexes["primary"]["infra"]["iops"]["write"]
                    }
            secondkeyschema["Projection"]={
                "ProjectionType": "ALL"
                }
            GlobalSecInd.append(secondkeyschema)
        paramstructure["GlobalSecondaryIndexes"]=GlobalSecInd
    return(paramstructure)
    
def createcf():
    datapath = "/home/app/web/archeplay/data"
    apipath=datapath + "/servicedesigns/"+serviceid+"/api/config.json"
    status,statusmessage,api=load_s3_file(apipath)
    if status == "error":
        message={"statusCode":400,"errorMessage":statusmessage}
        return(message)
    else:
        for ver in api["versions"]:
            versionid = ver["versionid"]
            TableProperties=[]
            for resourceid in ver["resources"]:
                resourcepath=datapath + "/servicedesigns/"+serviceid+"/api/"+versionid+"/resources/"+resourceid+"/config.json"
                resstatus,resstatusmessage,resource=load_s3_file(resourcepath)
                if resstatus == "success":
                    for data in resource["data"]:
                        for db in data["db"]:
                            dbid=db["Ref"]
                            dbpath=datapath + "/servicedesigns/"+serviceid+"/data/"+dbid+"/config.json"
                            dbstatus,dbstatusmessage,dbdata=load_s3_file(dbpath)
                            if dbstatus == "success":
                                for tableid in dbdata["tables"]:
                                    tablepath=datapath + "/servicedesigns/"+serviceid+"/data/"+dbid+"/tables/"+tableid+"/config.json"
                                    tbstatus,tbstatusmessage,tableconf=load_s3_file(tablepath)
                                    if tbstatus == "success":
                                        TableProperties.append(tableconf)
                                    else:
                                        message={"statusCode":400,"errorMessage":"tableconf error","Error":tableconf}
                                        return(message)
                            else:
                                message={"statusCode":400,"errorMessage":"dbdata error","Error":dbdata}
                                return(message)
    Tabledata=[]
    for tableconf in TableProperties:
        TableProperty=create_input(tableconf)
        Tabledata.append(TableProperty)
    ModuleTemplate={
                    "AWSTemplateFormatVersion": "2010-09-09",
                    "Resources": {},
                    "Outputs": {}
                }
    for prop in Tabledata:
        ModuleTemplate["Resources"].update({
            prop["TableName"]: {
                "Type": "AWS::DynamoDB::Table",
                "Properties": prop
            }
        })
        ModuleTemplate["Outputs"].update({
            prop["TableName"]+"output": {
                "Description": "Dynamodb TableName",
                "Value": {"Ref": prop["TableName"]}
                   
            }
        })
    modulepath=path+"/tablecf.json"
    f=open(modulepath,"w+")
    directory = os.path.dirname(modulepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    datastring=json.dumps(ModuleTemplate)
    data_folder=open(modulepath, "w")
    data_folder.write(datastring)

createcf()