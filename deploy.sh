#!/bin/sh

username=`cat ~/.scholadomi.username`

scp lectionarium.tar.gz $username@scholadomi.org:/home/$username/www

ssh $username@scholadomi.org <<EOF
rm -rf www/lectionarium
mkdir www/lectionarium
cd www/lectionarium
tar xf ../lectionarium.tar.gz
rm ../lectionarium.tar.gz
EOF
