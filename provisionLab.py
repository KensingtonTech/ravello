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
  print 'Usage: ' + sys.argv[0] + """ [OPTIONS]
  
Provision one or more Ravello applications from an existing blueprint. You will be prompted for a password.

Example: 

Options:
  -u, --user        Ravello username
  -n, --num         Number of Ravell applications to deploy.  There must be at least this number of applications defined in the configuration file
  -c, --conf        JSON configuration file to use.  This contains things like the application names, elastic IP info, and which VM names to start after deployment"""
  sys.exit(2)
  
  
  

def readConfFile(filename): #returns json object from configuration file
  try:
    with open(filename,'rb') as confFile:
      data = confFile.read()
  except:
    die("ERROR: error opening configuration file '" + filename + "'")
    
  try:
    cfg = json.loads(data)
    return cfg
  except:
    die("ERROR: error parsing configuration file '" + filename + "'.  Is your JSON formatted correctly?")




def main(user, num, confFile):
  confData = readConfFile(confFile)
  password = getpass.getpass('Password:')
  r = ravello(urlBase, user, password)
  
  if not "appDefinitions" in confData:
    die("ERROR: there is no 'appDefinitions' section in your configuration file")
  applications = confData['appDefinitions']
  
  if num > len(applications):
    die("ERROR: There aren't enough applications defined in your configuration file to deploy " + num + " applications")
    
  #CONFIRM WHETHER 'appName' AND 'blueprintName' KEYS EXIST
  for app in applications:
    if not "appName" in app:
      die("ERROR: There is no 'appName' key in your 'appDefinitions' section of your configuration file")

    if not "blueprintName" in app:
      die("ERROR: There is no 'blueprintName' key in your 'appDefinitions' section of your configuration file")
    
    if not r.blueprintExists(app['blueprintName']):
      die("ERROR: Blueprint " + app['blueprintName'] + " is not defined in Ravello.  Fix this and try again")
  
  #CHECK WHETHER ALL DEFINED ELASTIC IPS EXIST AND ARE FREE
  freeElasticIps = r.getFreeElasticIpList()
  i = 0
  while i < num:
    #for app in applications:
    app = applications[i]
    if 'elasticIps' in app:
      for elasticIpEntry in app['elasticIps']:
        if not ('elasticIpEntry' and 'ipAddress' and 'interfaceName') in elasticIpEntry:
          die("ERROR: keys 'vmName', 'ipAddress', and 'interfaceName' must all be defined in 'elasticIps' list")
        ipAddress  = elasticIpEntry['ipAddress']
        if not ipAddress in freeElasticIps:
          print "ERROR: " + elasticIpEntry['ipAddress'] + " is not a free Elastic IP for your Ravello account.  Free Elastic IP's are: "
          pprint(freeElasticIps)
          die("")
    i += 1

  #PUBLISH APPLICATIONS
  
  i = 0
  while i < num:
    #for app in applications:
    app = applications[i]
    appName = app['appName']
    blueprintName = app['blueprintName']
    desc = ''
    if 'appDescription' in app:
      desc = app['appDescription']

    #DEPLOY BLUEPRINT
    print "Deploying application '" + appName + "' from blueprint " + blueprintName
    try:
      r.deployBlueprint(blueprintName, appName, appDesc = desc)
    except urllib2.HTTPError, e:
      if e.code == 400:
        die("400 ERROR: application '" + appName + "' already exists or there is a problem with the creation parameters")
      elif e.code == 404:
        die("404 ERROR: blueprint '" + blueprintName + "' does not exist")
      else:
        die(str(e.code) + " ERROR: " + e.read())
    except:
      raise
      die("caught unhandled exception")

    #PUBLISH APP
    optimisation='COST_OPTIMIZED'
    if 'optimizeFor' in app:
      if app['optimizeFor'].lower() == 'cost':
        optimisation='COST_OPTIMIZED'
      if app['optimizeFor'].lower() == 'performance':
        optimisation='PERFORMANCE_OPTIMIZED'
      
    print "Publishing application '" + appName + "'"
    r.publishApplication(appName, optimisation)
    
    #SET APP COST BUCKET
    if 'costBucket' in app:
      costBucket = app['costBucket']
      print "Setting application cost bucket to '" + costBucket + "'"
      try:
        bucketCode = r.updateApplicationCostBucket( appName, costBucket )
      except urllib2.HTTPError, e:
        if e.code == 400:
          print "400 ERROR setting cost bucket: resource type not recognized.  You shouldn't ever see this error because resourceType is hard-coded to 'application'"
        elif e.code == 403:
          print "403 ERROR setting cost bucket: object doesn't exist, or EXECUTE permission not set on cost bucket, or READ permission not set on resource"
        elif e.code == 404:
          print "404 ERROR setting cost bucket: resource not found"
        else:
          print str(e.code) + " ERROR"
      except:
        print "ERROR: unknown exception"
   
    #Configure Elastic IP's
    if 'elasticIps' in app:
      elasticIps = app['elasticIps']
      for e in elasticIps:
        eVmName = e['vmName']
        ipAddress = e['ipAddress']
        interfaceName = e['interfaceName']
        print "Adding Elastic IP " + ipAddress + " to interface '" + interfaceName + "' of VM '" + eVmName + "'"
        r.addElasticIpToVm(appName, eVmName, interfaceName, ipAddress)
      #COMMIT APP CHANGES
      print "Committing changes to application '" + appName + "'"
      r.updateApplication(appName)
    
    #START VM's
    if 'vmsToStart' in app:
      vmsToStart = app['vmsToStart']
      for v in vmsToStart:
        print "Starting VM '" + v + "'"
        r.startVm(appName,v)
      
    #SET EXPIRY TIME FOR APP
    if 'stopTimeLimit' in app:
      stopTimeLimit = int(app['stopTimeLimit'])
      print "Setting expiration time of " + str(stopTimeLimit) + " minutes"
      r.setApplicationExpiryInMinutes(appName, stopTimeLimit)
      del stopTimeLimit
      
    i += 1
 
  
  #res = r.fetchUrl(path)
  #print(res)
  #print
  #data = json.loads(res)
  #pprint(data)
  #r.printApplications()
  #r.printElasticIps()
  #r.pprintElasticIps()
  #pprint(r.getElasticIpList())
  #pprint(r.getFreeElasticIpList())
  #r.printBlueprints()
  #print r.blueprintExists(blueprint)
  #print(r.getApplicationIdByName('SA 10.5 Training Lab'))
  #print r.deployBlueprint("SA 10.5 Training Lab - Embryonic - 2017.01.12-2", "Test", appDesc = 'Not much of a description')
  #print r.publishApplication('Test')
  #print(r.getApplicationByName('SA 10.5 Training Lab - 2017.01.12-2'))
  #print(str(r.getVmIdByName('SA 10.5 Training Lab - 2017.01.12-2','VPN')))
  #pprint(r.getVmDesign('SA 10.5 Training Lab - 2017.01.12-2','VPN'))
  #print(json.dumps(r.getVmDesign('Test','VPN')))
  #vm = r.getVmDesign('Test','VPN')
  #print r.addElasticIpToVm('Test','VPN','eth0-wan','153.92.32.69')
  #print r.updateApplication('Test')
  #r.startVms('Test',['UI','VPN'])
  #r.startVm('Test','Packet Player')
  #print r.setApplicationExpiryInHours('Test',2)
  #print r.setApplicationExpiryInMinutes('Test',60)
  #print r.deployBlueprint(blueprint, "Test")
  #print r.publishApplication('Test')
  #print r.addElasticIpToVm('Test','VPN','eth0-wan','153.92.32.69')
  #print r.updateApplication('Test')
  #print r.startVms('Test',['UI','VPN','Packet Player'])
  #print r.setApplicationExpiryInHours('Test',2)

if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:],"hu:n:c:",["user=","num=","conf="])
  except getopt.GetoptError:
    printOpts()

  for opt, arg in opts:
    if opt == '-h':
      printOpts()
    elif opt in ("-n", "--num"):
      if arg.isdigit():
        num=int(arg)
      else:
        die("ERROR: --num must be an integer")
    elif opt in ("-u", "--user"):
      user = arg
    elif opt in ("-c", "--conf"):
     confFile = arg
  if ('user' and 'num' and 'confFile') in globals() and isinstance( num, ( int, long ) ):
    main(user, num, confFile)
  else:
    printOpts()