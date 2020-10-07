# Adding a sheet to the Oracle Solaris Analytics Dashboard 

## Adding a sheet (.json file) via the Command Line Interface

The Oracle Solaris Analytics dashboard enables users to create custom sheets for monitoring and analyzing parameters ranging from performance as well as key StatsStore stats. Such custom sheets can be easily downloaded and shared amongst other users owing to the files being in a .json format. In order to add shared sheets to your personal dashboard, here are the steps:

### Step 1: Setting up the rsync client

For Windows and Mac OS, you need to have an rsync client installed in order to initiate remote file transfer to the server.

### Step 2: Locating the file location

In order to add the sheet to the remote machine and to the analytics dashboard, you need to first identify the location of the sheet on the local drive of your computer.

For Windows OS, using the command 

```
cd /mnt/c
```

will help you gain access to the folders on your personal storage.



### Step 3: Routing the file to the server

Once the file has been located,

/mnt/c/users/~~tdhuri~~/desktop/Solaris/GitHub Project/Sheets Samples/~~TanmayDhuri~~

use the following command to add your file to route your file to the IP address of your system.

```
rsync -avu 'SolarisDiscover.json' root@xx.xxx.xx.xx:.
```

Once the file has been routed, you can then proceed to adding the sheet to your custom dashboard.



### Step 4: Adding the sheet to view on custom dashboard

Once Step 3, is complete we need to remotely login to the server to copy the file into the webui library and restart the service for the file to be updated on the analytics dashboard.

#### 1) Locating the directory on Oracle Solaris where the sheet needs to be stored

The sheets being displayed on the Oracle Solaris Analytics dashboard are stored in 

```
cd /usr/lib/webui/analytics/sheets/site 
```

The new sheet (.json) file which was routed to the server needs to be moved to a location under the above directory.

#### 2) Adding the sheet to the directory

The sheets can be added to the above directory using

```
cp  ~/SolarisDiscover.json .
```

#### 3) Restarting the WebUI service to reflect the updates

Once the sheet has been added to the correct directory as mentioned above, the WebUI service needs to be restarted to reflect the updates on the web interface. The commands for the same are as follows:

```
root@:/usr/lib/webui/analytics/sheets/site# svcadm restart webui/server
root@:/usr/lib/webui/analytics/sheets/site# svcs -a | grep webui

```

Once the above service has been restarted successfully, you can login to the web interface to view the sheet on your personal dashboard.

Find a sample sheet [here](/StatsStore_WebUI/Sharing_Sheets/sample-sheet.json).

For a more in detailed sheet covering major statistics from the StatsStore, [click here](/StatsStore_WebUI/Sharing_Sheets/solaris-contrib.json).





Copyright (c) 2020, Oracle and/or its affiliates.
 Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.