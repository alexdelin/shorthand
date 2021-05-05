#!/bin/bash

set -e

if [[ $(ls ./js/*.br) ]]; then
    rm ./js/*.br
fi

brotli --best ./js/*.js
