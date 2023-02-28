#!/usr/bin/env bash
if [ "$POD_TYPE" == "webapp_backend" ]; then
    #TODO: remove this - needed for quick restarts for debugging
    # also remove git secrets env and volume mount from controller yaml
    mkdir $HOME/.ssh
    cp /etc/git-secret/* $HOME/.ssh/
    mv $HOME/.ssh/ssh $HOME/.ssh/id_rsa.git
    touch $HOME/.ssh/config

    # create git config file in .ssh
    echo "
    Host github.com
        Hostname github.com
        IdentityFile $HOME/.ssh/id_rsa.git
        IdentitiesOnly yes
    " > $HOME/.ssh/config

    # install aws-iam-authenticator
    curl -Lo aws-iam-authenticator https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.5.9/aws-iam-authenticator_0.5.9_linux_amd64
    chmod +x ./aws-iam-authenticator
    mkdir -p $HOME/bin && cp ./aws-iam-authenticator $HOME/bin/aws-iam-authenticator && export PATH=$PATH:$HOME/bin
    echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
    source ~/.bashrc

    # install kubectl
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

    # # install webapp dependencies
    # source /webapp/cerebro-ui/backend/init.sh

    # install requirements
    if [ -f /webapp/cerebro-ui/requirements.txt ]; then
        pip install -r /webapp/cerebro-ui/requirements.txt
    fi

    (cd /webapp/cerebro-kube/webapp && flask run --host=0.0.0.0 -p 8080  2>&1 |tee /webapp/cerebro-kube/webapp/webapp_logs.log)
# elif [ "$POD_TYPE" == "webapp_ui" ]; then
