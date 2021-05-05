#!/bin/bash

set -e

rm ./js/*.br
brotli --best ./js/*.js
