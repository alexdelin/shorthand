#!/bin/bash

set -e

if [[ $(ls ./js/*.br) ]]; then
    rm ./js/*.br
fi
if [[ $(ls ./css/*.br) ]]; then
    rm ./css/*.br
fi

brotli --best ./js/*.js
brotli --best ./css/*.css


if [[ $(ls ./js/*.gz) ]]; then
    rm ./js/*.gz
fi
if [[ $(ls ./css/*.gz) ]]; then
    rm ./css/*.gz
fi

gzip --best --keep ./js/*.js
gzip --best --keep ./css/*.css

