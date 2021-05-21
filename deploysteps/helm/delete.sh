#!/bin/bash

CLUSTERNAME=`jq -r '.Clustername' $TEMPLATE_PATH/$RESOURCEID/input.json`
Region=`jq -r '.AWSRegion' $TEMPLATE_PATH/$RESOURCEID/input.json`
aws eks update-kubeconfig --name $CLUSTERNAME --region $Region
helm uninstall $(helm list -aq)
