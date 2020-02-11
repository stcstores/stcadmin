#!/bin/bash

# shellcheck disable=SC1090

source "$(dirname "$(realpath "$0")")/env.sh"
sudo /bin/systemctl restart "gunicorn-$DOMAIN.service"
