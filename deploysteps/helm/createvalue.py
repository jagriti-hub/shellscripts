import json,yaml,sys,os

inputpath=sys.argv[1]
valuespath=sys.argv[2]

ImageName=os.getenv("ImageName")
f = open(inputpath,"r")
data = json.load(f)
data.update({"ImageName":ImageName})

f=open(valuespath+"/values.yaml","w+")
yaml.safe_dump(data,f,allow_unicode=True)