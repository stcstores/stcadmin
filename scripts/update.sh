#!/bin/bash

# Import local variables.
# shellcheck source=./env.sh
source "$(dirname "$(realpath "$0")")/env.sh"

#Set path variables
PROJECT_DIR="/home/stcstores/sites/$DOMAIN"
SOURCE_DIR="$PROJECT_DIR/source"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
LOG_DIR="$PROJECT_DIR/logs"
LOGFILE="$LOG_DIR/update.log"
CONFIG_DIR="$PROJECT_DIR/config"
CONFIG_FILE="$CONFIG_DIR/config.toml"
SECRET_KEY_FILE="$CONFIG_DIR/secret_key.toml"

# If a branch not matching $BRANCH is specified quit.
if [ ! -z "$1" ]; then
  if [ ! $1 = $BRANCH ]; then
    exit 0
  fi
fi
NEW_COMMIT="$2"


# Create log file. This is done after the branch check so an empty file is not written
# if a non matching branch is specified.
DATE=`date '+%Y-%m-%d %H:%M:%S'`
echo "$DATE" > $LOGFILE
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>>$LOGFILE 2>&1

# Ensure the environment is built with a predictable path.
export PIPENV_VENV_IN_PROJECT=true

#Update git repo
cd $SOURCE_DIR || exit 1
echo "Cleaning git repo..."
git fetch
git clean -f
git reset --hard HEAD

echo "Updating git repo..."
if [ ! -z "$NEW_COMMIT" ]; then
  echo "Updating $DOMAIN source to commit $NEW_COMMIT"
  git checkout -f $NEW_COMMIT
else
  echo "Updating $DOMAIN source to tip of $BRANCH"
  git checkout -f $BRANCH
fi

UPDATED_COMMIT=`git log -n 1 --pretty=format:'%h %s'`
echo "Updated to commit $UPDATED_COMMIT"

#Set up python environment.
echo "Building environment..."
make production-init

# Quit with error if no config file exists.
if [ ! -f $CONFIG_FILE ]; then
  echo "ERROR: Config file does not exist at $CONFIG_FILE. Exiting..."
  exit 1
fi

# Create a secret key file if none exists.
if [ ! -f $SECRET_KEY_FILE ]; then
  echo "WARNING: Secret key file not found at $SECRET_KEY_FILE."
  echo "Generating a new secret key file..."
  SECRET_KEY=`cat /dev/urandom | tr -dc 'a-zA-Z0-9(){}!$^&' | fold -w 50 | head -n 1`
  echo "SECRET_KEY = \"$SECRET_KEY\"" > $SECRET_KEY_FILE
fi

# Build the docs.
echo "Building docs..."
make docs

# Update static files.
echo "Collecting static files..."
pipenv run python manage.py collectstatic --noinput

# Migrate the database.
echo "Migrating database..."
pipenv run python manage.py migrate --noinput

# Restart the site with the new version.
echo "Restarting service..."
$SCRIPTS_DIR/restart.sh

echo "$DOMAIN is new using commit $UPDATED_COMMIT"
