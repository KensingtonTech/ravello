#!/bin/bash

# Gets the detailed blueprints for a ravello organisation in raw format

USER=''
PASSWD=''
ORGID=''
BASEURL='https://cloud.ravellosystems.com/api/v1'

images=''

for x in $images; do
  curl -u $USER:$PASSWD $BASEURL/blueprints/$x
done