#!/bin/bash

# Gets all Ravello disk image definitions for an account in raw format

USER=''
PASSWD=''
ORGID=''
BASEURL='https://cloud.ravellosystems.com/api/v1'

images=''

for x in $images; do
  curl -u $USER:$PASSWD $BASEURL/images/$x
done