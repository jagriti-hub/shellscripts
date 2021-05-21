#!/bin/bash

SERVICEID=$1
STACK_NAME="table-"$SERVICEID
TEMPLATE_PATH=$CLONE_PATH

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
    pkgs='awscli jq gettext bash-completion moreutils zip unzip'
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
        sudo apt install -y $pkgs
    fi
elif [ $OSTYPE == "redhat" ]
then
    pkgs='awscli jq gettext bash-completion moreutils zip unzip'
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

REGION=`cat inputoption.json | jq -r '.Region.value'`

###Install Python PIP3 AWSCLI
if [ $OSTYPE == "ubuntu" ]
then
    if [ -x "$(command -v python3)" ]; then
        echo "python3 is already installed"
        #Check if package installed
        if [ -x "$(command -v pip3)" ]; then
            echo "pip3 is already installed"
            #python module awscli installation
            if [ -x $(command -v pip3 show awscli) ]; then
                echo "pip3 module awscli is installed"
                # sudo pip3 install --upgrade awscli && hash -r
            else
                echo "Python3 PIP"
                sudo pip3 install awscli boto3 botocore
            fi
        else
            echo "Install pip3"
            echo "Python3 PIP installation"
            sudo apt install python3-pip
            pip3 --version
            #python module awscli installation
            if [ -x $(command -v pip3 show awscli) ]; then
                echo "pip3 module awscli is installed"
                # sudo pip3 install --upgrade awscli && hash -r
            else
                echo "Python3 PIP"
                sudo pip3 install awscli boto3 botocore
            fi
        fi
    else
        echo "Install python3"
        sudo apt update -y
        sudo apt install -y software-properties-common
        sudo add-apt-repository ppa:deadsnakes/ppa
        sudo apt update -y
        sudo apt install python3.8
        python3 --version
        #Check if package pip3 installed
        if [ -x "$(command -v pip3)" ]; then
            echo "pip3 is already installed"
            #python module awscli installation
            if [ -x $(command -v pip3 show awscli) ]; then
                echo "pip3 module awscli is installed"
                # sudo pip3 install --upgrade awscli && hash -r
            else
                echo "Python3 PIP"
                sudo pip3 install awscli boto3 botocore
            fi
        else
            echo "Install pip3"
            echo "Python3 PIP installation"
            sudo apt install python3-pip
            pip3 --version
            #python module awscli installation
            if [ -x $(command -v pip3 show awscli) ]; then
                echo "pip3 module awscli is installed"
                # sudo pip3 install --upgrade awscli && hash -r
            else
                echo "Python3 PIP"
                sudo pip3 install awscli boto3 botocore
            fi
        fi
    fi
elif [ $OSTYPE == "redhat" ]
then
    if [ -x "$(command -v python3)" ]; then
        echo "python3 is already installed"
        #Check if package installed
        if [ -x "$(command -v pip3)" ]; then
            echo "pip3 is already installed"
            #python module awscli installation
            if [ -x $(command -v pip3 show awscli) ]; then
                echo "pip3 module awscli is installed"
                # sudo pip3 install --upgrade awscli && hash -r
            else
                echo "Python3 PIP"
                sudo pip3 install awscli boto3 botocore
            fi
        else
            echo "Install pip3"
            echo "Python3 PIP installation"
            sudo yum install python3-pip
            pip3 --version
            #python module awscli installation
            if [ -x $(command -v pip3 show awscli) ]; then
                echo "pip3 module awscli is installed"
                # sudo pip3 install --upgrade awscli && hash -r
            else
                echo "Python3 PIP"
                sudo pip3 install awscli boto3 botocore
            fi
        fi
    else
        echo "Install python3"
        sudo yum update -y
        sudo yum install python3
        python3 --version
        #Check if package pip3 installed
        if [ -x "$(command -v pip3)" ]; then
            echo "pip3 is already installed"
            #python module awscli installation
            if [ -x $(command -v pip3 show awscli) ]; then
                echo "pip3 module awscli is installed"
                # sudo pip3 install --upgrade awscli && hash -r
            else
                echo "Python3 PIP"
               sudo pip3 install awscli boto3 botocore
            fi
        else
            echo "Install pip3"
            echo "Python3 PIP installation"
            sudo yum install python3-pip
            pip3 --version
            #python module awscli installation
            if [ -x $(command -v pip3 show awscli) ]; then
                echo "pip3 module awscli is installed"
                # sudo pip3 install --upgrade awscli && hash -r
            else
                echo "Python3 PIP"
                sudo pip3 install awscli boto3 botocore
            fi
        fi
    fi
fi


python3 ${TEMPLATE_PATH}/PATHPARAM/getloadbalancervpclink.py $REGION $SERVICEID

if [ -z "$1" ]
  then
    echo "No STACK_NAME argument given. Please provide StackName"
    exit 1
fi

echo "Creating stack "$STACK_NAME" please wait..."
STACK_ID=$( \
  aws cloudformation create-stack \
  --stack-name ${STACK_NAME} \
  --template-body file://${TEMPLATE_PATH}/PATHPARAM/apigwcf.json \
  --parameters file://${TEMPLATE_PATH}/PATHPARAM/input.json --region $REGION\
  | jq -r .StackId \
)