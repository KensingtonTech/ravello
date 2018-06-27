import urllib2
import base64
import json
from pprint import pprint

class ravello:
  
  def __init__(self, url, user, password):
    self.url = url
    self.user = user
    self.password = password
    self.org = self.getOrgId()
    self.syncApplications()
    self.syncImages()
    self.syncElasticIps()
    self.syncBlueprints()
    self.syncCostBuckets()



  def getUrl(self,path): #HTTP GET
    request=urllib2.Request(self.url + path)
    base64string = base64.b64encode('%s:%s' % (self.user, self.password))
    request.add_header("Authorization", "Basic %s" % base64string)  
    request.add_header('Content-type','application/json') 
    request.add_header('Accept','application/json')
    result = urllib2.urlopen(request)
    return result.read()



  def postUrl(self,path,body): #HTTP POST
    request=urllib2.Request(self.url + path)
    base64string = base64.b64encode('%s:%s' % (self.user, self.password))
    request.add_header("Authorization", "Basic %s" % base64string)  
    request.add_header('Content-type','application/json') 
    request.add_header('Accept','application/json')
    result = urllib2.urlopen(request,body)
    return result.getcode()



  def putUrl(self,path,body): #HTTP PUT
    request=urllib2.Request(self.url + path, data=body)
    base64string = base64.b64encode('%s:%s' % (self.user, self.password))
    request.add_header("Authorization", "Basic %s" % base64string)  
    request.add_header('Content-type','application/json') 
    request.add_header('Accept','application/json')
    request.get_method = lambda: 'PUT'
    result = urllib2.urlopen(request,body)
    return result.getcode()






  #####ORGANISATION#####

  def getOrgId(self):
    res = self.getUrl('/organization')
    orgData = json.loads(res)
    return str(orgData['id'])



  def printOrgId(self):
    print self.org





  
  #####VM IMAGES#####

  def syncImages(self):
    # private images
    self.rawImages = self.getUrl('/organizations/' + self.org + '/images')
    self.images = json.loads(self.rawImages)



  def pprintImages(self):
    pprint(self.images)



  def syncImagesDetailed(self):
    # call me manually
    detailedImages = []
    for image in self.images:
      id = image['id']
      #print id
      detailedImages.append( self.getImageById(id) )
    self.detailedImages = detailedImages



  def pprintImagesDetailed(self):
    pprint(self.detailedImages)
  


  def getImageById(self, id):
    rawImage = self.getUrl('/images/' + str(id))
    image = json.loads(rawImage)
    return image






  #####DISK IMAGES#####

  def syncDiskImages(self):
    # run manually
    rawDiskImages = self.getUrl('/diskImages')
    self.diskImages = json.loads(rawDiskImages)



  def pprintDiskImages(self):
    pprint(self.diskImages)



  def pprintPrivateDiskImages(self):
    privateDiskImages = []
    for x in self.diskImages:
      if not x['isPublic']:
        privateDiskImages.append(x)
    pprint(privateDiskImages)






  #####APPLICATIONS#####    

  def syncApplications(self):
    self.rawApplications = self.getUrl('/applications')
    self.applications = json.loads(self.rawApplications)



  def pprintApplications(self):
    #self.syncApplications()
    pprint(self.applications)



  def printApplications(self):
    #self.syncApplications()
    print(self.rawApplications)



  def getApplicationIdByName(self,n):
    #self.syncApplications()
    for a in self.applications:
      if a['name'] == n :
        return a['id']
    return



  def publishApplication(self,n,optimizationLevel): #valid optimizationLevel values are COST_OPTIMIZED or PERFORMANCE_OPTIMIZED
    id=self.getApplicationIdByName(n)
    if id == None:
      return False
    path='/applications/' + str(id) + '/publish/'
    data = { "optimizationLevel": optimizationLevel,    "startAllVms": "false" }
    code = self.postUrl(path,json.dumps(data))
    self.syncApplications()
    if code != 202:
      print code
      return False
    return True



  def getApplicationByName(self,n):
    id = self.getApplicationIdByName(n)
    path = '/applications/' + str(id) + ';design'
    application = self.getUrl(path)
    return json.loads(application)



  def updateApplication(self,appName):
    appId = self.getApplicationIdByName(appName)
    path = '/applications/' + str(appId) + '/publishUpdates?startAllDraftVms=false'
    return self.postUrl(path,'')



  def setApplicationExpiryInHours(self,appName,hours):
    appId = self.getApplicationIdByName(appName)
    path = '/applications/' + str(appId) + '/setExpiration'
    params = { 'expirationFromNowSeconds' : hours * 60 * 60 }
    return self.postUrl(path,json.dumps(params))



  def setApplicationExpiryInMinutes(self,appName,minutes):
    appId = self.getApplicationIdByName(appName)
    path = '/applications/' + str(appId) + '/setExpiration'
    params = { 'expirationFromNowSeconds' : minutes * 60 }
    return self.postUrl(path,json.dumps(params))






  #####Application VM's#####

  def getVmIdByName(self, appName, vmName):
    application = self.getApplicationByName(appName)
    vms = application['design']['vms']
    for v in vms:
      if v['name'] == vmName:
        return v['id']
    return



  def getVmDesignByName(self, appName, vmName):
    appId = self.getApplicationIdByName(appName)
    vmId = self.getVmIdByName(appName,vmName)
    path = '/applications/' + str(appId) + '/vms/' + str(vmId)
    vm = self.getUrl(path)
    return json.loads(vm)



  def getVmDesignById(self, appId, vmId):
    path = '/applications/' + str(appId) + '/vms/' + str(vmId)
    vm = self.getUrl(path)
    #print vm
    return json.loads(vm)



  def updateVmByName(self, appName, vmName, vmObj):
    appId = self.getApplicationIdByName(appName)
    vmId = self.getVmIdByName(appName, vmName)
    path='/applications/' + str(appId) + '/vms/' + str(vmId)
    return self.putUrl(path,json.dumps(vmObj))



  def updateVmById(self,appId,vmId,vmObj):
    path='/applications/' + str(appId) + '/vms/' + str(vmId)
    return self.putUrl(path,json.dumps(vmObj))



  def getVmNicByName(self,vm,nicName):
    num=0
    for n in vm['networkConnections']:
      if n['name'] == nicName:
        return num
      num += 1
    return



  def addElasticIpToVm(self,appName,vmName,nicName,ip):
    appId = self.getApplicationIdByName(appName)
    vmId = self.getVmIdByName(appName, vmName)
    path = '/applications/' + str(appId) + '/vms/' + str(vmId)
    vm = self.getVmDesignById(appId, vmId) #vm is json object representing a virtual machine
    nicPos=self.getVmNicByName(vm, nicName)
    vm['networkConnections'][nicPos]['ipConfig']['needElasticIp'] = True
    vm['networkConnections'][nicPos]['ipConfig']['hasPublicIp'] = True
    vm['networkConnections'][nicPos]['ipConfig']['externalAccessState'] = 'ALWAYS_PUBLIC_IP'
    vm['networkConnections'][nicPos]['ipConfig']['elasticIpAddress'] = ip
    return self.updateVmById(appId, vmId, vm)
  


  def startVm(self,appName,vmName):
    appId = self.getApplicationIdByName(appName)
    vmId = self.getVmIdByName(appName, vmName)
    path = '/applications/' + str(appId) + '/vms/' + str(vmId) + '/start'
    return self.postUrl(path, '')



  def startVms(self,appName,vmNameList):
    appId = self.getApplicationIdByName(appName)
    vmIds = [self.getVmIdByName(appName,v) for v in vmNameList]
    path = '/applications/' + str(appId) + '/vms/start'
    i = { 'ids' : vmIds }
    return self.postUrl(path, json.dumps(i))






  #####ELASTIC IP's#####

  def syncElasticIps(self):
    self.rawElasticIps = self.getUrl('/elasticIps')
    self.elasticIps = json.loads(self.rawElasticIps)



  def pprintElasticIps(self):
    #self.syncElasticIps()
    pprint(self.elasticIps)



  def printElasticIps(self):
    #self.syncElasticIps()
    print(self.rawElasticIps)



  def getElasticIpList(self):
    #self.syncElasticIps()
    ipList = [i['ip'] for i in self.elasticIps]
    return ipList



  def getFreeElasticIpList(self):
    #self.syncElasticIps()
    ipList = [ i['ip'] for i in self.elasticIps if not 'ownerAppId' in i ]
    return ipList





   
  #####BLUEPRINTS#####

  def syncBlueprints(self):
    # gets high-level private blueprints
    self.rawBlueprints = self.getUrl('/organizations/' + self.org + '/blueprints')
    self.blueprints = json.loads(self.rawBlueprints)



  def getBlueprintByName(self, n):
    #self.syncBlueprints()
    for b in self.blueprints:
      if b['name'] == n :
        return b['id']
    return



  def pprintBlueprints(self):
    #self.syncBlueprints()
    pprint(self.blueprints)



  def syncBlueprintsDetailed(self):
    # run manually
    detailedBlueprints = []
    for x in self.blueprints:
      id = x['id']
      detailedBlueprints.append(self.getBlueprintById(id)) 
    self.blueprintsDetailed = detailedBlueprints
      


  def getBlueprintById(self, id):
    raw = self.getUrl('/blueprints/' + str(id))
    return json.loads(raw)



  def pprintBlueprintsDetailed(self):
    pprint(self.blueprintsDetailed)



  def printBlueprints(self):
    #self.syncBlueprints()
    print(self.rawBlueprints)



  def blueprintExists(self,bp):
    #self.syncBlueprints()
    for b in self.blueprints:
      if b['name'] == bp:
        return True
    return False



  def deployBlueprint(self, bpname, appName, appDesc = ''):
    path='/applications'
    bpid=self.getBlueprintByName(bpname)
    if not bpid:
      return False
    data = { "name": appName, "description" : appDesc, "baseBlueprintId": bpid }
    code = self.postUrl(path,json.dumps(data))
    self.syncApplications()
    if code != 201:
      print code
      return False
    return True






  #####COST BUCKETS#####

  def syncCostBuckets(self):
    rawCostBuckets = self.getUrl('/costBuckets')
    self.costBuckets = json.loads(rawCostBuckets)



  def getCostBucketIdByName(self,n):
    for b in self.costBuckets:
      if b['name'] == n :
        return b['id']
    return



  def updateApplicationCostBucket(self,appName,costBucketName):
    appId = self.getApplicationIdByName(appName)
    costBucketId = self.getCostBucketIdByName(costBucketName)
    path='/costBuckets/' + str(costBucketId) + '/associateResource'
    resourceObj = {}
    resourceObj['resourceId'] = appId
    resourceObj['resourceType'] = 'application'
    return self.putUrl( path, json.dumps(resourceObj) )
    
