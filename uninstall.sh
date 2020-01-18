#!/bin/bash

rm -rf /etc/apps/shorthand
rm -rf /var/log/apps/shorthand
rm -rf /var/run/apps/shorthand

deactivate
rmvirtualenv shorthand
