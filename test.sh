#!/bin/bash
. environment.sh
thisdir="$( cd "$( dirname "$0" )" && pwd )"
python -m unittest discover -s "$thisdir/python/test" -p "test_*.py"
