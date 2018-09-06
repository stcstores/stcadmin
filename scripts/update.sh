#!/bin/bash

# Import local variables.
# shellcheck source=./env.sh
source "$(dirname "$(realpath "$0")")/env.sh"
# Sets DOMAIN, BRANCH, PROJECT DIR and PATH

#Set path variables
SOURCE_DIR="$PROJECT_DIR/source"
GIT_DIR="$SOURCE_DIR/.git"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
LOG_DIR="$PROJECT_DIR/logs"
LOGFILE="$LOG_DIR/update.log"
CONFIG_DIR="$PROJECT_DIR/config"
CONFIG_FILE="$CONFIG_DIR/config.toml"
SECRET_KEY_FILE="$CONFIG_DIR/secret_key.toml"

# If a branch not matching $BRANCH is specified quit.
if [ ! -z "$1" ]; then
  if [ ! $1 == $BRANCH ]; then
    exit 0
  fi
fi
NEW_COMMIT="$2"

# Create log file. This is done after the branch check so an empty file is not written
# if a non matching branch is specified.
DATE=`date '+%Y-%m-%d %H:%M:%S'`
printf "$DATE\n\n" > $LOGFILE #  Clear log file and add the current time and date.
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>>$LOGFILE 2>&1  # Redirect stdout and stder to log file.

# Write current variables to log file.
printf "Passed branch argument: '$1'\n"
printf "Passed Commit argument: '$2'\n"
printf "Project: $PROJECT_DIR\n"
printf "Gitpath: $GIT_DIR\n"
printf "Domain: $DOMAIN\n"
printf "Project branch: $BRANCH\n"
printf "Default python executable: `which python`\n"
printf "Current commit: `git --git-dir $GIT_DIR log -n 1 --pretty=format:'%h %s'`\n\n"

# Ensure the environment is built with a predictable path.
export PIPENV_VENV_IN_PROJECT=true

#Update git repo
printf "\nCleaning git repo...\n"
git --git-dir $GIT_DIR fetch
git --git-dir $GIT_DIR clean -f
git --git-dir $GIT_DIR reset --hard HEAD

printf "\nUpdating git repo...\n"
if [ ! -z "$NEW_COMMIT" ]; then
  printf "Updating $DOMAIN source to commit $NEW_COMMIT\n"
  git --git-dir $GIT_DIR checkout -f $NEW_COMMIT
else
  printf "Updating $DOMAIN source to tip of $BRANCH\n"
  git --git-dir $GIT_DIR checkout -f "origin/$BRANCH"
fi

UPDATED_COMMIT=`git --git-dir $GIT_DIR log -n 1 --pretty=format:'%h %s'`
printf "\nUpdated to commit $UPDATED_COMMIT\n"

#Set up python environment.
printf "\nBuilding environment...\n"
make production-init

# Quit with error if no config file exists.
if [ ! -f $CONFIG_FILE ]; then
  printf "\nERROR: Config file does not exist at $CONFIG_FILE. Exiting...\n"
  exit 1
fi

# Create a secret key file if none exists.
if [ ! -f $SECRET_KEY_FILE ]; then
  printf "\nWARNING: Secret key file not found at $SECRET_KEY_FILE.\n"
  printf "Generating a new secret key file...\n"
  SECRET_KEY=`cat /dev/urandom | tr -dc 'a-zA-Z0-9(){}!$^&' | fold -w 50 | head -n 1`
  echo "SECRET_KEY = \"$SECRET_KEY\"" > $SECRET_KEY_FILE
fi

# Build the docs.
printf "\nBuilding docs...\n"
make docs

# Update static files.
printf "\nCollecting static files...\n"
pipenv run python manage.py collectstatic --noinput

# Migrate the database.
printf "\nMigrating database...\n"
pipenv run python manage.py migrate --noinput

# Restart the site with the new version.
printf "\nRestarting service...\n"
$SCRIPTS_DIR/restart.sh

printf "\nComplete. $DOMAIN is new using commit $UPDATED_COMMIT\n"
