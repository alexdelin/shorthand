#!/bin/bash

set -e

export VERSION="0.2.0"

cd react-frontend/
npm run build
cd ..

docker build \
    --tag alexdelin/shorthand:${VERSION} \
    --platform linux/arm64 \
    --push \
    .
