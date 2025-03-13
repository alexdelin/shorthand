#!/bin/bash

set -e

export VERSION="0.1.1"

cd react-frontend/
npm run build
cd ..

docker build \
    --tag alexdelin/shorthand:${VERSION} \
    --platform linux/arm/v7 \
    --push \
    .
