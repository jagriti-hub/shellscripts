#!/bin/bash
TEMPLATE_PATH=$CLONE_PATH

REGION=`jq -r '.AWSRegion' input.json`
ACCOUNTID=`jq -r '.AWSAccountId' input.json`
SERVICEID=`jq -r '.serviceid' input.json`
TAG=`jq -r '.Tag' input.json`

#Docker Installation
if [ -x "$(command -v docker)" ]; then
  echo "docker is installed"
else
  echo "Install docker"
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  usermod -aG docker ubuntu
fi

#Describe and Create ECR registry
aws ecr describe-repositories --repository-names $(jq -r '.resources[]' input.json)
if [ $? == 0 ]
then
  echo "REPOSITORIES Already Existed"
else
  for RESOURCEID  in `jq -r '.resources[]' input.json `
  do
    # Create repo
    aws ecr create-repository --repository-name $RESOURCEID
    if [ $? ==0 ]
    then
      echo "$RESOURCEID REPOSITORY CREATED"
    else
      echo "$RESOURCEID CREATION FAILED"
    fi
  done
fi

#DOCKER LOGIN"
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNTID.dkr.ecr.$REGION.amazonaws.com
if [ $? == 0 ]
then
  echo "DOCKER LOGIN SUCCESS"
  #BUILD IMAGES
  for RESOURCEID  in `jq -r '.resources[]' input.json `
  do
    #BUILD image
    docker build -t $RESOURCEID ${TEMPLATE_PATH}/PATHPARAM/${SERVICEID}/${RESOURCEID}
    if [ $? == 0 ]
    then
      echo "DOCKER BUILD SUCCESS"
    else
      echo "DOCKER BUILD FAILED"
    fi

    #TAG
    docker tag $RESOURCEID:latest $ACCOUNTID.dkr.ecr.$REGION.amazonaws.com/$RESOURCEID:$TAG
    if [ $? == 0 ]
    then
      echo "DOCKER TAG SUCCESS"
      #PUSH
      docker push $ACCOUNTID.dkr.ecr.$REGION.amazonaws.com/$RESOURCEID:$TAG
      if [ $? == 0 ]
      then
        echo "DOCKER PUSH SUCCESS"
      else
        echo "DOCKER PUSH FAILED"
      fi
    else
      echo "DOCKER TAG FAILED"
    fi
  done
else
  echo "DOCKER LOGIN FAILED"
fi