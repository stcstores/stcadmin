#!/bin/bash

# shellcheck disable=SC1090

source "$(dirname "$(realpath "$0")")/env.sh"
/home/stcstores/sites/$DOMAIN/source/.venv/bin/gunicorn --timeout=300 --workers=5 --bind unix:/tmp/$DOMAIN.socket stcadmin.wsgi:application
