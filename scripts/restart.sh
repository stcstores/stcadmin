#!/bin/bash

source "$(dirname "$(realpath "$0")")/env.sh"
sudo systemctl restart gunicorn-$DOMAIN.service
