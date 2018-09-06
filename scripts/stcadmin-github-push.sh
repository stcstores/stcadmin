#!/bin/bash

REF="$1"
COMMIT="$2"
BRANCH=`basename "$REF"`
/home/stcstores/sites/staging.stcadmin.stcstores.co.uk/scripts/update.sh $BRANCH $COMMIT
/home/stcstores/sites/stcadmin.stcstores.co.uk/scripts/update.sh $BRANCH $COMMIT
