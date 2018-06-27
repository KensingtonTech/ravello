# Python and shell scripts and library for working with Ravello Cloud via the Ravello API

These scripts were developed as part of a project I worked on.  I can't be bothered to package it properly as a Python library.  I am unfortunately unable to provide support for them, but they are provided for your benefit.


* ravello.py contains the class Ravello.  This can be used to fetch data on VM's, VM Images, Applications, Blueprints, etc.

* getBlueprints.py - Gets all high-level private blueprint definitions for a Ravello organisation in JSON format

* getBlueprintsDetailed.py - Gets all detailed private blueprint definitions for a Ravello organisation in JSON format

* getBlueprintsDetailedRaw.sh - Gets the detailed blueprints for a ravello organisation in raw format

* getDiskImages.py - Gets all Ravello disk image definitions for an account in JSON format

* getImagesRaw.sh - Gets all Ravello disk image definitions for an account in raw format

* getOrgId.py - Gets the Ravello org ID for an account

* getVMImages.py - Gets all high-level Ravello VM image definitions for an account in JSON format

* getVMImagesDetailed.py - Gets all detailed Ravello VM image definitions for an account in JSON format

* provisionLab.py - Provisions one or more applications from a configuration file, using pre-existing blueprint, N number of times.

** Lab Provision Config file

```json
{
  "appDefinitions" : [
    { 
      "appName" : "Application Name 1",
      "blueprintName" : "My Blueprint Name",
      "optimizeFor" : "performance",
      "costBucket" : "My Cost Bucket",
      "vmsToStart" : [ "VM 1", "VM 2" ],
      "elasticIps" : [ {
                          "vmName" : "VPN",
                          "ipAddress" : "1.1.1.1",
                          "interfaceName" : "eth0"
                        } ]
    },
    ...Add additional here as required
  ]
}
```