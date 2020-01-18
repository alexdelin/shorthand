#!/bin/bash

export APP_USER=$(whoami)
export APP_GROUP='pi'
export CONFIG_LOCATION=/etc/apps/shorthand/shorthand_config.json

# Make dirs and place default config
sudo mkdir /etc/apps
sudo chown ${APP_USER}:${APP_GROUP} /etc/apps
mkdir /etc/apps/shorthand
cp sample_config.json ${CONFIG_LOCATION}

# Make dirs for log files
sudo mkdir /var/log/apps
sudo chown ${APP_USER}:${APP_GROUP} /var/log/apps
mkdir /var/log/apps/shorthand

# Make dir for pid file
sudo mkdir /var/run/apps
sudo chown ${APP_USER}:${APP_GROUP} /var/run/apps
mkdir /var/run/apps/shorthand

mkvirtualenv -p $(which python3.7) shorthand
pip install -r requirements.txt
python setup.py develop
