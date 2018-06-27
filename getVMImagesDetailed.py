#!/usr/bin/env python

import sys
import json
import getopt
import getpass
from ravello import ravello
from pprint import pprint
import urllib2

urlBase='https://cloud.ravellosystems.com/api/v1'

confData={}

def die(text):
  print text
  sys.exit(1)



def printOpts():
  print 'Usage: ' + sys.argv[0] + """ -u <username>
  
Gets all detailed Ravello VM image definitions for an account in JSON format."""
  sys.exit(2)



def main(user):
  password = getpass.getpass('Password:')
  rav = ravello(urlBase, user, password)
  getImageDetailed(rav)



def getImageDetailed(rav):
  rav.syncImagesDetailed()
  rav.pprintImagesDetailed()



if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:],"hu:",["user="])
  except getopt.GetoptError:
    printOpts()

  for opt, arg in opts:
    if opt == '-h':
      printOpts()
    elif opt in ("-u", "--user"):
      user = arg
  if 'user' in globals():
    main(user)
  else:
    printOpts()