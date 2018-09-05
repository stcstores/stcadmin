#!/bin/bash

source "$(dirname "$(realpath "$0")")/env.sh"

PROJECT_DIR="/home/stcstores/sites/$DOMAIN"
SOURCE_DIR="$PROJECT_DIR/source"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
LOG_DIR="$PROJECT_DIR/logs"
LOGFILE="$LOG_DIR/update.log"
CONFIG_DIR="$PROJECT_DIR/config"
CONFIG_FILE="$CONFIG_DIR/config.toml"
SECRET_KEY_FILE="$CONFIG_DIR/secret_key.toml"

if [ ! -z "$1" ]; then
        if [ ! $1 = $BRANCH ]; then
                exit 0
        fi
fi


DATE=`date '+%Y-%m-%d %H:%M:%S'`
echo "$DATE" > $LOGFILE
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>>$LOGFILE 2>&1

export PIPENV_VENV_IN_PROJECT=true
cd $SOURCE_DIR || exit 1
echo "Updating $DOMAIN..."
echo "Checking out branch $BRANCH..."
git fetch
git checkout -f $BRANCH
NEW_COMMIT=`git log -n 1 --pretty=format:'%h %s'`
echo "Updated to commit $NEW_COMMIT"
echo "Building environment..."
make re-init

if [ ! -f $CONFIG_FILE ]; then
	echo "ERROR: Config file does not exist at $CONFIG_FILE. Exiting..."
	exit 1
fi
if [ ! -f $SECRET_KEY_FILE ]; then
        echo "WARNING: Secret key file not found at $SECRET_KEY_FILE."
	echo "Generating a new secret key file..."
        SECRET_KEY=`cat /dev/urandom | tr -dc 'a-zA-Z0-9(){}!$^&' | fold -w 50 | head -n 1`
        echo "SECRET_KEY = \"$SECRET_KEY\"" > $SECRET_KEY_FILE
fi

echo "Building docs..."
make docs

echo "Collecting static files..."
pipenv run python manage.py collectstatic --noinput

echo "Migrating database..."
pipenv run python manage.py migrate --noinput

echo "Restarting service..."
$SCRIPTS_DIR/restart.sh

echo "$DOMAIN is up to date with branch $BRANCH. Now using commit $NEW_COMMIT"
