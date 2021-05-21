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

### Install packages ####
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
                sudo pip3 install awscli
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
                sudo pip3 install awscli
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
                sudo pip3 install awscli
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
                sudo pip3 install awscli
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
                sudo pip3 install awscli
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
                sudo pip3 install awscli
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
                sudo pip3 install awscli
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
                sudo pip3 install awscli
            fi
            
        fi
    fi
fi

#Install EKSCTL
which eksctl && eksctl version
if [ $? == 0 ]; then
  echo "eksctl is already installed"
else
  echo "Install eksctl"
  curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
  sudo mv /tmp/eksctl /usr/local/bin
  eksctl version
fi

### Install kubectl
# which kubectl && kubectl version
if [ -x "$(command -v kubectl)" ]; then
    echo "kubectl is already installed"
else
    echo "Install kubectl"
    sudo curl --silent --location -o /usr/local/bin/kubectl \
    https://amazon-eks.s3.us-west-2.amazonaws.com/1.17.11/2020-09-18/bin/linux/amd64/kubectl
    sudo chmod +x /usr/local/bin/kubectl

    #Install yq for yaml processing
    echo 'yq() {
    docker run --rm -i -v "${PWD}":/workdir mikefarah/yq "$@"
    }' | tee -a ~/.bashrc && source ~/.bashrc

    #Verify the binaries are in the path and executable
    for command in kubectl jq envsubst aws
    do
        which $command &>/dev/null && echo "$command in path" || echo "$command NOT FOUND"
    done

    #Enable kubectl bash_completion
    echo "Enable kubectl bash_completion"
    kubectl completion bash >>  ~/.bash_completion
    . /etc/profile.d/bash_completion.sh
    . ~/.bash_completion
    echo "Enable kubectl bash_completion DONE"

    #set the AWS Load Balancer Controller version
    echo "Enable EXPORT LBC"
    echo 'export LBC_VERSION="v2.0.0"' >>  ~/.bash_profile
    . ~/.bash_profile
    echo "Enable EXPORT LBC DONE"
fi

TEMPLATE_PATH=$CLONE_PATH

for RESOURCEID  in `jq -r '.resources[]' ./resinput.json`
do
    unzip $TEMPLATE_PATH/PATHPARAM/chart.zip -d $TEMPLATE_PATH/PATHPARAM/$RESOURCEID/
    CLUSTERNAME=`jq -r '.Clustername' $TEMPLATE_PATH/PATHPARAM/$RESOURCEID/input.json`
    Region=`jq -r '.AWSRegion' $TEMPLATE_PATH/PATHPARAM/$RESOURCEID/input.json`
    echo $Region
    echo $CLUSTERNAME
    aws eks update-kubeconfig --name $CLUSTERNAME --region $Region
    helm install -f $TEMPLATE_PATH/PATHPARAM/$RESOURCEID/values.yaml $TEMPLATE_PATH/PATHPARAM/$RESOURCEID/mychart --generate-name
done