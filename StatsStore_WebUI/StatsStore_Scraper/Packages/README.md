# Packages

This directory contains pre-built packages of the examples that can be used as is. For any additional requirements please see the information about relevant examples in the **[Build Environment](../Build_Environment)** directory.

## The Splunk StatsStore Scraper packages

The **[Splunk example](../Build_Environment/Splunk_Example.md)** allows you to push StatsStore data into the Splunk HTTP Event Collector (HEC). The steps to create the package by hand see the **[StatsStore Scraper structure](StatsStore_Scraper_Structure.md)** document. This directory contains `p5p` archive files with the prebuilt package. The file is called `sstore_scraper.p5p`.

### How to install, configure, and run

To use the package you can either use the individual `p5p` file to install from or you can upload the `p5p` file into a local IPS repository. 

#### Single p5p file install

To install the package on the system either copy the `p5p` file to the destination system or for example put it on an NFS share. Become the `root` user or a user with the privileges to install packages and navigate to the directory that holds the `p5p` file. Next install the package:

```bash
# pkg install -g ./sstore_scraper.p5p sstore_scraper
WARNING: The boot environment being modified is not the active one.  Changes
made will not be reflected on the next boot.

           Packages to install:  1
            Services to change:  1
       Create boot environment: No
Create backup boot environment: No

DOWNLOAD                                PKGS         FILES    XFER (MB)   SPEED
Completed                                1/1           5/5      0.0/0.0 47.4k/s

PHASE                                          ITEMS
Installing new actions                         16/16
Updating package state database                 Done 
Updating package cache                           0/0 
Updating image state                            Done 
Creating fast lookup database                   Done 
Updating package cache                           4/4 
```

#### Uploading to IPS repository

For details on how to upload the package to an IPS repository you can either use the steps mentioned in the **[StatsStore Scraper structure](StatsStore_Scraper_Structure.md)** document, or use the steps shown in [Deliver to a Package Repository](https://docs.oracle.com/cd/E53394_01/html/E54820/pkgcreate.html#PKDEVpkgdelivery). Now you can use the regular `pkg install`:

```bash
# pkg install sstore_scraper
           Packages to install:  6
           Mediators to change:  1
            Services to change:  1
       Create boot environment: No
Create backup boot environment: No

DOWNLOAD                                PKGS         FILES    XFER (MB)   SPEED
Completed                                6/6     1755/1755    18.0/18.0  8.2M/s

PHASE                                          ITEMS
Installing new actions                     1883/1883
Updating package state database                 Done 
Updating package cache                           0/0 
Updating image state                            Done 
Creating fast lookup database                   Done 
Updating package cache                           2/2 
```

In this case the system is also pulling in dependency packages.

#### Configure

Next get the connection data for the Splunk HEC. You'll need the HEC hostname/IP address and port number, as well as the authorization key associated with the metric in Splunk that data needs to feed into. Take these an fill them into the `/opt/sstore_scraper/etc/server_info.yaml` file:

```yaml
servers:
    localhost:
        server_port: "local"

agent:
    interval: 60

destination:
    splunk:
        # configure the IP address and port for the Splunk HEC
        server_endpoint: '<splunk_ip_address>:<splunk_hec_port>'
        request_type: 'POST'
        request_transport: 'https://'
        request_uri: '/services/collector'
        headers: 
            # Insert the authorization key
            Authorization: 'Splunk <splunk_authorization_key>'
        data_template:
            event: 'metric'
            source: 'metrics'
            sourcetype: 'solaris_statsstore_metrics'
            fields:
                os: 'Oracle Solaris'
                # optional data
                # datacenter: 'North'
                # rack: '42'
                # team: 'Time Bandits'
```

Where you can also add any other identifying fields for that system in the `fields:` section.

#### Run

Now the configuration has been done, enable the service:

```bash
# svcadm enable sstore-scraper
# svcs -lp sstore-scraper
fmri         svc:/site/sstore-scraper:default
name         site/sstore-scraper
enabled      true
state        online
next_state   none
state_time   2022-09-21T15:06:38
logfile      /var/svc/log/site-sstore-scraper:default.log
restarter    svc:/system/svc/restarter:default
contract_id  173 
manifest     /lib/svc/manifest/site/sstore_scraper.xml
dependency   require_all/none svc:/milestone/multi-user (online)
process      1266 /usr/bin/python3 /opt/sstore_scraper/bin/sstore_scraper.py
```

The service is now up and data should be showing up in Splunk.

### Versions

The current version is v0.3.

```bash
# pkg info -g ./sstore_scraper.p5p sstore_scraper
          Name: stats/statsstore/sstore_scraper
       Summary: The StatsStore Scraper pulls data from the Oracle Solaris
                StatsStore, converts the data, and exports this into something
                like the Splunk HEC
   Description: StatsStore Scraper and Exporter
      Category: System/Administration and Configuration
         State: Not installed
     Publisher: scraper
       Version: 0.3
        Branch: None
Packaging Date: Wed Sep 21 17:26:49 2022
          Size: 20.75 kB
          FMRI: pkg://scraper/stats/statsstore/sstore_scraper@0.3:20220921T172649Z
```

Copyright (c) 2022 Oracle and/or its affiliates and released under the [Universal Permissive License (UPL)](https://oss.oracle.com/licenses/upl/), Version 1.0