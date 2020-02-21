#!/bin/bash

rm -rf /etc/apps/shorthand
rm -rf /var/log/apps/shorthand
rm -rf /var/run/apps/shorthand
rm /tmp/shorthand.sock
rm /etc/uwsgi/sites/shorthand_uwsgi_conf.ini
rm /etc/nginx/sites-available/shorthand
rm /etc/nginx/sites-enabled/shorthand

sudo systemctl stop shorthand
sudo systemctl disable shorthand
sudo systemctl restart nginx

rm /etc/systemd/system/shorthand.service

deactivate
rmvirtualenv shorthand
