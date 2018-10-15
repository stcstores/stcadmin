#!/bin/bash

PROJECT_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
DOMAIN="$(basename $PROJECT_DIR)"  # The domain of the site. Used in file paths.
export BRANCH
export PROJECT_DIR
export DOMAIN

# shellcheck source=/home/$USER/.pythonpaths
source ~/.pythonpaths  # Set path to python executables.
