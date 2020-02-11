#!/bin/bash

REF="$1"
COMMIT="$2"
BRANCH=$(basename "$REF")
if [ "$BRANCH" == "develop" ]; then
  "/home/<username>/sites/staging.<sitename>/scripts/update.sh $COMMIT"
fi
if [ "$BRANCH" == "master" ]; then
  "/home/<username>/sites/<sitename>/scripts/update.sh $COMMIT"
fi
