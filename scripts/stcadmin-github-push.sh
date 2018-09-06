#!/bin/bash

REF="$1"
COMMIT="$2"
BRANCH=`basename "$REF"`
if [ "$BRANCH" == "future" ]; then
  /home/stcstores/sites/staging.stcadmin.stcstores.co.uk/scripts/update.sh $COMMIT
fi
if [ "$BRANCH" == "master" ]; then
  /home/stcstores/sites/stcadmin.stcstores.co.uk/scripts/update.sh $COMMIT
fi
