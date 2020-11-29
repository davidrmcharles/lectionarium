#!/bin/sh
rm -rf lectionarium.tar.gz
tar --create --gzip --file=lectionarium.tar.gz --directory=build .
