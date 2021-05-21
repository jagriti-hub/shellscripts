#!/bin/bash
TEMPLATE_PATH=$CLONE_PATH

REGION=`jq -r '.AWSRegion' input.json`
ACCOUNTID=`jq -r '.AWSAccountId' input.json`
SERVICEID=`jq -r '.serviceid' input.json`
TAG=`jq -r '.Tag' input.json`
echo $REGION
echo $ACCOUNTID
echo $SERVICEID

