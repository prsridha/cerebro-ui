#!/bin/bash

# update apt for future package installs
apt update

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
    source /data/cerebro-ui/backend/backend_init.sh

    # install requirements
    if [ -f /data/cerebro-ui/requirements.txt ]; then
        pip install -r /data/cerebro-ui/requirements.txt
    fi

    (cd /data/cerebro-ui/backend && flask run --host=0.0.0.0 -p 8083  2>&1 |tee /data/cerebro-ui/backend/backend_logs.log)
    # sleep infinity
elif [ "$POD_TYPE" == "webapp_ui" ]; then
    echo "
    export const environment = {
        backendURL: 'http://$BACKEND_HOST:30083'
    };
    " | tee /data/cerebro-ui/project-cerebro/src/environments/environment.ts /data/cerebro-ui/project-cerebro/src/environments/environment.development.ts

    (cd /data/cerebro-ui/project-cerebro && npm install)
    (export NG_CLI_ANALYTICS="false" && cd /data/cerebro-ui/project-cerebro && ng serve --host 0.0.0.0 --port 80 --disable-host-check)
    # sleep infinity
fi