#!/bin/bash

BRANCH=""  # The site will be updated when changes are commited to this path.

if [ -z "$BRANCH" ]; then
  echo "Branch not set."
  exit 1
fi

PROJECT_DIR="$(realpath "$(dirname "$(dirname "$0")")")"
DOMAIN="$(basename $PROJECT_DIR)"  # The domain of the site. Used in file paths.
export BRANCH
export PROJECT_DIR
export DOMAIN

# shellcheck source=/home/$USER/.pythonpaths
source ~/.pythonpaths  # Set path to python executables.
