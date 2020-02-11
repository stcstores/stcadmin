#!/bin/bash

# shellcheck disable=SC1090

PROJECT_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
DOMAIN="$(basename "$PROJECT_DIR")"
export BRANCH
export PROJECT_DIR
export DOMAIN

source ~/.pythonpaths
source ~/.poetry/env
