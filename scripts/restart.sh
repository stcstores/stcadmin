#!/bin/bash

source env.sh
sudo systemctl restart gunicorn-$DOMAIN.service
