#!/bin/bash
which apt > /dev/null
if [ $? -eq 0 ]
then
  OSTYPE=ubuntu
else
  which yum > /dev/null
  if [ $? -eq 0 ]
  then
    OSTYPE=redhat
  else
    OSTYPE=unknown
  fi
fi
echo $OSTYPE
### Install jq ####
if [ $OSTYPE == "ubuntu" ]
then
  pkgs='jq awscli'
  install=false
  for pkg in $pkgs; do
    echo $pkg
    status="$(dpkg-query -W --showformat='${db:Status-Status}' "$pkg" 2>&1)"
    echo $status
    if [ ! $? = 0 ] || [ ! "$status" = installed ]; then
      install=true
      break
    fi
  done
  if "$install"; then
    sudo apt -yinstall $pkgs
  fi
elif [ $OSTYPE == "redhat" ]
then
  pkgs='jq awscli'
  install=false
  for pkg in $pkgs; do
    echo $pkg
    status="$(dpkg-query -W --showformat='${db:Status-Status}' "$pkg" 2>&1)"
    echo $status
    if [ ! $? = 0 ] || [ ! "$status" = installed ]; then
      install=true
      break
    fi
  done
  if "$install"; then
    sudo yum -y install $pkgs
  fi
fi

TEMPLATE_PATH=$CLONE_PATH
SERVICEID=$2
STACK_NAME=$SERVICEID"-VPC"
REGION=`jq -r '.AWSRegion' $TEMPLATE_PATH/PATHPARAM/input.json`
echo $REGION

echo ${STACK_NAME}

echo "Updating stack "$STACK_NAME" please wait..."
STACK_ID=$( \
  aws cloudformation update-stack \
  --stack-name ${STACK_NAME} \
  --template-body file://${TEMPLATE_PATH}/PATHPARAM/vpc.yaml \
  --parameters file://${TEMPLATE_PATH}/PATHPARAM/parameters.json --region $REGION\
  | jq -r .StackId \
)

echo "Waiting on ${STACK_ID} update completion..."

cloudformation_tail() {
  local lastEvent
  local lastEventId
  local stackStatus=$(aws cloudformation describe-stacks --region $REGION --stack-name $STACK_NAME | jq -c -r .Stacks[0].StackStatus)
  until \
    [ "$stackStatus" = "CREATE_COMPLETE" ] \
    || [ "$stackStatus" = "CREATE_FAILED" ] \
    || [ "$stackStatus" = "DELETE_COMPLETE" ] \
    || [ "$stackStatus" = "DELETE_FAILED" ] \
    || [ "$stackStatus" = "ROLLBACK_COMPLETE" ] \
    || [ "$stackStatus" = "ROLLBACK_FAILED" ] \
    || [ "$stackStatus" = "UPDATE_COMPLETE" ] \
    || [ "$stackStatus" = "UPDATE_ROLLBACK_COMPLETE" ] \
    || [ "$stackStatus" = "UPDATE_ROLLBACK_FAILED" ]; do

    #[[ $stackStatus == *""* ]] || [[ $stackStatus == *"CREATE_FAILED"* ]] || [[ $stackStatus == *"COMPLETE"* ]]; do
    lastEvent=$(aws cloudformation describe-stack-events --region $REGION --stack $STACK_NAME --query 'StackEvents[].{ EventId: EventId, LogicalResourceId:LogicalResourceId, ResourceType:ResourceType, ResourceStatus:ResourceStatus, Timestamp: Timestamp }' --max-items 1 | jq .[0])
    eventId=$(echo "$lastEvent" | jq -r .EventId)
    if [ "$eventId" != "$lastEventId" ]
    then
      lastEventId=$eventId
      echo $(echo $lastEvent | jq -r '.Timestamp + "\t-\t" + .ResourceType + "\t-\t" + .LogicalResourceId + "\t-\t" + .ResourceStatus')
    fi
    sleep 3
    stackStatus=$(aws cloudformation describe-stacks --region $REGION --stack-name $STACK_NAME | jq -c -r .Stacks[0].StackStatus)
    aws cloudformation describe-stacks --stack-name ${STACK_ID} --region $REGION | jq .Stacks[0].Outputs > ${TEMPLATE_PATH}/PATHPARAM/output.json
  done
  echo "Stack Status: $stackStatus"
}

cloudformation_tail $SERVICE_STACK_NAME $REGION