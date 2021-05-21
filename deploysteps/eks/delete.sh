#!/bin/bash
TEMPLATE_PATH=$1

kubectl delete -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.3.6/components.yaml
kubectl delete -f ${TEMPLATE_PATH}/ingresscontroller.yaml
eksctl delete cluster -f ${TEMPLATE_PATH}/eksconfig.yaml