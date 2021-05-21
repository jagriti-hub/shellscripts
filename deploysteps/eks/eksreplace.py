import os,sys,time,json
templatepath=sys.argv[1]
filepath=templatepath+"/eksctl.yaml"
inputpath=templatepath+"/input.json"
ekspath=templatepath+"/eksconfig.yaml"

with open(filepath, "r+") as f:
    eksyaml = f.read()

with open(inputpath, "r+") as f:
    input_options = json.loads(f.read())

with open("vpcoutput.json",'r') as f:
    vpcoutputfile = json.loads(f.read())

vpcoutput={}
for dic in vpcoutputfile:
    ip = { str(dic["OutputKey"]) : str(dic["OutputValue"]) }
    vpcoutput.update(ip)
# print(vpcoutput)


PrivateSubnetId1=vpcoutput["PrivateSubnet1ID"]
PrivateSubnetId2=vpcoutput["PrivateSubnet2ID"]
PublicSubnetId1=vpcoutput["PublicSubnet1ID"]
PublicSubnetId2=vpcoutput["PublicSubnet2ID"]
Region=vpcoutput["VPCRegion"]
PrivateAvailabilityZone1=vpcoutput["PrivateAvailabilityZone1"]
PrivateAvailabilityZone2=vpcoutput["PrivateAvailabilityZone2"]
PublicAvailabilityZone1=vpcoutput["PublicAvailabilityZone1"]
PublicAvailabilityZone2=vpcoutput["PublicAvailabilityZone2"]

eksyaml=eksyaml.replace("PVTSUBNETID1",PrivateSubnetId1)
eksyaml=eksyaml.replace("PVTSUBNETID2",PrivateSubnetId2)
eksyaml=eksyaml.replace("PUBSUBNETID1",PublicSubnetId1)
eksyaml=eksyaml.replace("PUBSUBNETID2",PublicSubnetId2)
eksyaml=eksyaml.replace("PVTAZ1",PrivateAvailabilityZone1)
eksyaml=eksyaml.replace("PVTAZ2",PrivateAvailabilityZone2)
eksyaml=eksyaml.replace("PUBAZ1",PublicAvailabilityZone1)
eksyaml=eksyaml.replace("PUBAZ2",PublicAvailabilityZone2)
eksyaml=eksyaml.replace("AWSREGION",Region)
eksyaml=eksyaml.replace("CLUSTERNAME",input_options["Clustername"])
eksyaml=eksyaml.replace("DESIREDCAPACITY",str(input_options["DesiredCapacity"]))
eksyaml=eksyaml.replace("INSTANCETYPE",str(input_options["InstanceType"]))
eksyaml=eksyaml.replace("MAXSIZE",str(input_options["MaxSize"]))
eksyaml=eksyaml.replace("MINSIZE",str(input_options["MinSize"]))
eksyaml=eksyaml.replace("NGNAME",input_options["NodeGrpName"])
eksyaml=eksyaml.replace("VOLUME",str(input_options["Volume"]))
eksyaml=eksyaml.replace("KEYPAIRNAME",input_options["KeyName"])

data_folder=open(ekspath,"w+")
data_folder.write(eksyaml)