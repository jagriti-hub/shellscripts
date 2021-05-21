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


TEMPLATE_PATH=$1
STACK_NAME=$SERVICEID"-VPC"
REGION=`jq -r '.AWSRegion' $TEMPLATE_PATH/PATAHPARAM/input.json`

echo "Deleting stack "$STACK_NAME" please wait..."
## DELETE CLOUDFORMATION STACK
echo 'Deleting the stack...'
aws cloudformation delete-stack --stack-name $STACK_NAME
echo 'Waiting for the stack to be deleted, this may take a few minutes...'
aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME
echo 'Deleting stack "$STACK_NAME" completed'
