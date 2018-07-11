#!/bin/bash
thisdir="$( cd "$( dirname "$0" )" && pwd )"
. $thisdir/environment.sh
$thisdir/../python/lectionary.py $@
