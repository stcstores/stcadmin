#!/bin/bash

source env.sh
/home/stcstores/sites/$DOMAIN/source/.venv/bin/gunicorn --timeout=300 --workers=5 --bind unix:/tmp/$DOMAIN.socket stcadmin.wsgi:application
