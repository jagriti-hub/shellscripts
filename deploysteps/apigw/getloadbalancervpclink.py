import boto3,os,json,sys
templatepath="/home/ec2-user/environment"
# templatepath=sys.argv[1]
Region=sys.argv[1]

input_options={
    "Clustername": "testcluster"
}
# inputpath=templatepath+"/input.json"
# Region=os.getenv("VPCRegion")
# with open(inputpath, "r+") as f:
#     input_options = json.load(f)
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
        status={"status":"success","LoadBalancerDNS": LoadBalancerDNS}
        return(status)
    except Exception as e:
        status={"status":"error","errorMessage":str(e)}
        return(status)
        
def getvpclink():
    try:
        apigwclient=boto3.client('apigateway',region_name=Region)
        response = apigwclient.get_vpc_links()
        for vpclink in response["items"]:
            if vpclink["name"] == input_options["Clustername"]+"_vpclink":
                VpclinkID = vpclink["id"]
                print(VpclinkID)
        status={"status":"success","VpclinkID": VpclinkID}
        return(status)
    except Exception as e:
        status={"status":"error","errorMessage":str(e)}
        return(status)
        
def main():
    status=getloadbalancer()
    if status["status"] == "error":
        message={"status":"error","errorMessage":status["errorMessage"]}
        return(message)
    LoadBalancerDNS=status["LoadBalancerDNS"]
    vpclinkstatus=getvpclink()
    print(vpclinkstatus)
    if vpclinkstatus["status"] == "error":
        message={"status":"error","errorMessage":vpclinkstatus["errorMessage"]}
        return(message)
    message={"status":"success","message":"vpclinkcreated"}
    VpclinkID=vpclinkstatus["VpclinkID"]
    output = [
        {
            "ParameterKey": "LoadBalancerDNS",
            "ParameterValue": "http://" + LoadBalancerDNS
        }, 
        {
            "ParameterKey": "VpclinkID",
            "ParameterValue": VpclinkID
        }
    ]
    with open(templatepath+"/input.json","a") as f:
        f.write(json.dumps(output))
    status={"status":"success","body": "successfully got the details of load balancer dns and vpclink id"}
finalstatus=main()