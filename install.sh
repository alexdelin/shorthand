#!/bin/bash

export APP_USER='pi'
export APP_GROUP='pi'
export CONFIG_LOCATION=/etc/apps/shorthand/shorthand_config.json

# Make dirs and place default config
sudo mkdir /etc/apps
sudo chown ${APP_USER}:${APP_GROUP} /etc/apps
mkdir /etc/apps/shorthand
cp sample_config.json ${CONFIG_LOCATION}

sudo mkdir -p /etc/uwsgi/sites
sudo chown ${APP_USER}:${APP_GROUP} /etc/uwsgi/sites
cp uwsgi/shorthand_uwsgi_conf.ini /etc/uwsgi/sites/shorthand_uwsgi_conf.ini

# Make dirs for log files
sudo mkdir /var/log/apps
sudo chown ${APP_USER}:${APP_GROUP} /var/log/apps
mkdir /var/log/apps/shorthand

# Make dir for pid file
sudo mkdir /var/run/apps
sudo chown ${APP_USER}:${APP_GROUP} /var/run/apps
mkdir /var/run/apps/shorthand

# Create a new Virtualenv and install the shorthand package
mkvirtualenv -p $(which python3.7) shorthand
pip install -r requirements.txt
python setup.py develop

# Install Nginx
sudo apt install nginx
sudo cp nginx/shorthand.conf /etc/nginx/sites-available/shorthand
sudo ln -s /etc/nginx/sites-available/shorthand /etc/nginx/sites-enabled/shorthand

# Add the pi user to the www-data group
sudo usermod -a -G www-data pi

# Set up as a service
sudo cp systemd/shorthand.service /etc/systemd/system/shorthand.service

# Start / Restart services
sudo systemctl start shorthand
sudo systemctl restart nginx

# Enable services to run on boot
sudo systemctl enable shorthand
sudo systemctl enable nginx
