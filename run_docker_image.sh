#!/bin/bash

set -e

export VERSION="0.1.1"

docker run \
    --publish 127.0.0.1:8181:8181 \
    alexdelin/shorthand:${VERSION}
