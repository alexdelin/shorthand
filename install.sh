#!/bin/bash

export APP_USER='pi'
export APP_GROUP='pi'
export CONFIG_LOCATION=/etc/shorthand/shorthand_config.json

# Make dirs and place default config
sudo mkdir /etc/shorthand
sudo chown ${APP_USER}:${APP_GROUP} /etc/shorthand
cp sample_config.json ${CONFIG_LOCATION}

cp web/uwsgi/shorthand.ini /etc/uwsgi/sites/shorthand.ini

# Make dirs for log files
sudo mkdir /var/log/shorthand
sudo chown ${APP_USER}:${APP_GROUP} /var/log/shorthand

# Create a new Virtualenv and install the shorthand package
mkvirtualenv -p $(which python3.7) shorthand
pip install -r requirements.txt
python setup.py develop

# Deploy Nginx site
sudo cp web/nginx/shorthand.conf /etc/nginx/sites-available/shorthand
sudo ln -s /etc/nginx/sites-available/shorthand /etc/nginx/sites-enabled/shorthand

# Set up as a service
sudo cp web/systemd/uwsgi.service /etc/systemd/system/uwsgi.service

# Start / Restart services
sudo systemctl start shorthand
sudo systemctl restart nginx

# Enable services to run on boot
sudo systemctl enable shorthand
sudo systemctl enable nginx
