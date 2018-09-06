#!/bin/bash

# shellcheck source=./env.sh
source "$(dirname "$(realpath "$0")")/env.sh"
sudo systemctl restart gunicorn-$DOMAIN.service
