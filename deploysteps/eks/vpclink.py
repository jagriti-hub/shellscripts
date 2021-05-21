import boto3,os,json,sys

templatepath=sys.argv[1]
inputpath=templatepath+"/input.json"
with open(inputpath, "r+") as f:
    input_options = json.loads(f.read())
Region=input_options["AWSRegion"]
    
def getloadbalancer():
    try:
        client = boto3.client('resourcegroupstaggingapi',region_name=Region)
        response = client.get_resources(
            TagFilters=[
                {
                    'Key': 'kubernetes.io/service-name',
                    'Values': [
                        'ingress-nginx/ingress-nginx-controller',
                    ]
                },
                {
                    'Key': 'kubernetes.io/cluster/'+input_options["Clustername"],
                    'Values': [
                        'owned',
                    ]
                }
            ],
            ResourceTypeFilters=[
                'elasticloadbalancing:loadbalancer',
            ]
        )
        
        loadbalancerarn=response["ResourceTagMappingList"][0]["ResourceARN"]
        
        lbclient = boto3.client('elbv2',region_name=Region)
        
        lbresponse = lbclient.describe_load_balancers(
            LoadBalancerArns=[
                loadbalancerarn,
            ]
        )
        LoadBalancerDNS=lbresponse["LoadBalancers"][0]["DNSName"]
        output={
            "LoadBalancerDNS":LoadBalancerDNS
        }
        with open(templatepath+"/output.json","a") as f:
            f.write(output)
        status={"status":"success","body":loadbalancerarn}
        return(status)
    except Exception as e:
        status={"status":"error","errorMessage":str(e)}
        return(status)
        
def createvpclink(loadbalancerarn):
    try:
        apigwclient=boto3.client('apigateway',region_name=Region)
        vpclink = apigwclient.create_vpc_link(
            name=input_options["Clustername"]+"_vpclink",
            targetArns=[
                loadbalancerarn
            ]
        )
        
        VpclinkID = vpclink["id"]
        output={
            "VpclinkID":VpclinkID
        }
        describevpclink = apigwclient.get_vpc_link(
            vpcLinkId=VpclinkID
        )
        vpclinkstatus=describevpclink["status"]
        while vpclinkstatus in ["PENDING"]:
            describevpclink = apigwclient.get_vpc_link(
                vpcLinkId=VpclinkID
            )
            vpclinkstatus=describevpclink["status"]
        with open(templatepath+"/output.json","a") as f:
            f.write(output)
        status={"status":"success","body":VpclinkID}
        return(status)
    except Exception as e:
        status={"status":"error","errorMessage":str(e)}
        return(status)

def main():
    status=getloadbalancer()
    if status["status"] == "error":
        message={"status":"error","errorMessage":status["errorMessage"]}
        return(message)
    loadbalancerarn=status["body"]
    vpclinkstatus=createvpclink(loadbalancerarn)
    if vpclinkstatus == "error":
        message={"status":"error","errorMessage":vpclinkstatus["errorMessage"]}
        return(message)
    message={"status":"success","message":"vpclinkcreated"}

finalstatus=main()