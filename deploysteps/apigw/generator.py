import sys,os,boto3,time,math,random
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

def create_input(apigwconf):
    serviceid = apigwconf["serviceid"]
    servicename = apigwconf["servicename"]
    ModuleTemplate={
        "AWSTemplateFormatVersion": "2010-09-09",
        "Parameters": {},
        "Resources": {},
        "Outputs": {}
    }
    ModuleTemplate["Resources"]={
        "api" + serviceid:{
            "Type" : "AWS::ApiGateway::RestApi",
            "Properties" : {
              "EndpointConfiguration" : {"Types": ["EDGE"]},
              "Name" : apigwconf["servicename"]
            }
        },
        "resource" + serviceid:{
            "Type" : "AWS::ApiGateway::Resource",
            "Properties" : {
              "ParentId" : { "Fn::GetAtt": ["api" + serviceid, "RootResourceId"] },
              "PathPart" : "{proxy+}",
              "RestApiId" : {"Ref": "api" + serviceid}
            }
        },
        "deployment" + serviceid:{
            "Type" : "AWS::ApiGateway::Deployment",
            "DependsOn": ["method" + serviceid],
            "Properties" : {
              "RestApiId" : {"Ref": "api" + serviceid},
              "StageName" : servicename
            }
        }
    }
    if "cognitouserpoolarn" in apigwconf:
        method_authorizer_output={
            "method" + serviceid:{
                "Type" : "AWS::ApiGateway::Method",
                "DependsOn": ["authorizer" + serviceid],
                "Properties" : {
                    "AuthorizationType" : "COGNITO_USER_POOLS",
                    "AuthorizerId": {"Ref": "authorizer" + serviceid},
                    "HttpMethod" : "ANY",
                    "RequestParameters" : {"method.request.path.proxy": True},
                    "Integration" : {
                        "Uri": {"Fn::Join": ["", [{"Ref": "LoadBalancerDNS" }, "/", {"Ref": "servicename"}, "/{proxy}"]]},
                        "Type" : "HTTP_PROXY",
                        "RequestParameters": {"integration.request.path.proxy": "method.request.path.proxy"},
                        "IntegrationHttpMethod" : "ANY", 
                        "ConnectionId" : {"Ref": "VpclinkID"},
                        "ConnectionType" : "VPC_LINK"
                    },
                    "MethodResponses" : [{"StatusCode" : "200"}],
                    "ResourceId" : {"Ref": "resource" + serviceid},
                    "RestApiId" : {"Ref": "api" + serviceid}
                }
            },
            "authorizer" + serviceid:{
                "Type" : "AWS::ApiGateway::Authorizer",
                "Properties" : {
                    "ProviderARNs" : [apigwconf["cognitouserpoolarn"]],
                    "RestApiId" : {"Ref": "api" + serviceid},
                    "Type" : "COGNITO_USER_POOLS",
                    "IdentitySource": "method.request.header.auth",
                    "Name": "authorizer" + serviceid
                }
            }
        }
        ModuleTemplate["Resources"].update(method_authorizer_output)
    ModuleTemplate["Outputs"].update({
        "Invokeurl": {
            "Description": "invoke url for calling api",
            "Value": {"Fn::Join": ["", ["https://", {"Ref": "api" + serviceid}, ".execute-api.", {"Ref": "AWS::Region"}, ".amazonaws.com/", servicename]]}
               
        }
    })
    ModuleTemplate["Parameters"]= {
        "LoadBalancerDNS": {
            "Description": "Give the load balancer dns name of load balancer",
            "Type": "String",
            "Default": "http://archeplay.amazonaws.com"
        },
        "VpclinkID": {
            "Description": "Give the vpc link id",
            "Type": "String",
            "Default": "vpc176480"
        },
        "servicename":{
            "Type": "String",
            "Default": servicename
        }
    }
    return(ModuleTemplate)
    


def createcf():
    datapath = "/home/app/web/archeplay/data"
    apipath = datapath + "/servicedesigns/"+serviceid+"/api/config.json"
    status,statusmessage,api=load_s3_file(apipath)
    if status == "error":
        message={"statusCode":400,"errorMessage":statusmessage}
        return(message)
    apiuserinput = path + "/inputoption.json"
    status,statusmessage,apiinput=load_s3_file(apiuserinput)
    if status == "error":
        message={"statusCode":400,"errorMessage":statusmessage}
        return(message)
    apigwconf={
        "serviceid": serviceid,
        "servicename": api["apiname"],
        "cognitouserpoolarn": apiinput["Cognitouserpoolarn"]["value"]
    }
    ModuleTemplate=create_input(apigwconf)
    modulepath=path+"/apigwcf.json"
    f=open(modulepath,"w+")
    directory = os.path.dirname(modulepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    datastring=json.dumps(ModuleTemplate)
    data_folder=open(modulepath, "w")
    data_folder.write(datastring)

createcf()