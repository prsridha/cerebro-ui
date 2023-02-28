#!/bin/bash

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

if [ "$POD_TYPE" == "webapp_backend" ]; then
    # install webapp dependencies
    source /webapp/cerebro-ui/backend/backend_init.sh

    # install requirements
    if [ -f /webapp/cerebro-ui/requirements.txt ]; then
        pip install -r /webapp/cerebro-ui/requirements.txt
    fi

    # (cd /webapp/cerebro-ui/backend && flask run --host=0.0.0.0 -p 8080  2>&1 |tee /webapp/cerebro-ui/backend/backend_logs.log)
    sleep infinity
elif [ "$POD_TYPE" == "webapp_ui" ]; then
    (cd /webapp/cerebro-ui/project-cerebro && npm install)
    # (export NG_CLI_ANALYTICS="false" && cd /webapp/cerebro-ui/project-cerebro && ng serve --host 0.0.0.0 --port 80)
    sleep infinity
fi