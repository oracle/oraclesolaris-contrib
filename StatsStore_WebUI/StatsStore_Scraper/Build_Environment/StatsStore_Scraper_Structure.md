# The StatsStore Scraper Structure

This document explains the main elements of the Scraper and how it generally works. It is written in Python 3 and was developed and tested with Python 3.7 on Oracle Solaris 11.4 on both SPARC and x86 systems.

## Main script

The main script had three main functions:

* Pull data from the StatsStore through RAD
* Convert and simplify the data
* Export the data

The following sections will explain each function

### Pull data from the StatsStore through RAD

As the main goal of the StatsStore Scraper is pulling data from the Oracle Solaris StatsStore, the first step has to be to connect to the StatsStore. This can be done either locally on the Oracle Solaris instance over `rad:local` or remotely to other Oracle Solaris instances over their `rad:remote` service. The Scraper script is intended to be able to do either but initially is focused on running on the Oracle Solaris instances and connecting locally. The remote vs local discussion is interesting but for a later time. Both have pro's and con's.

The Scraper script used the RAD/REST service to connect to the StatsStore. To do this it has to pass a JSON datagram to RAD that looks like this:

```json
{
    "ssids": [<list of SSIDs>],
    "range": {
        "range_type": "RANGE_BY_TIME",
        "range_by_time": {
            "start_ts": -1,
            "end_ts": -1,
            "step": 1
        },   
        "show_unstable": true,
        "show_unbrowsable": true 
    }
}
```

This will return the values for the SSIDs in the `<list of SSIDs>` at the moment of the request. The `-1` in `"start_ts"` and `"end_ts"` indicate "now". 

### Convert and simplify the data

The response will be a JSON datagram with the data in a fairly complex nested form, something that is ideal for programmatic use, like the Oracle Solaris WebUI, but less optimal for passing on to data collection tools that expect all the information about one data point in one line. This is why the Scraper script will take the JSON data and reduce it to the core things it needs: The name of the data, the value of the data, and the timestamp it was collected. 

Similarly, the name of the SSIDs is fairly long, maybe confusing, and filled with characters that might trip up the ingest engine. So for example it will allow the conversion from  `//:class.cpu//:stat.fpu-usage//:op.rate` to `cpu_fpu-usage_rate`. The exact name conversion can be controlled through the export mechanism as different tools use different conventions. 

One other thing the conversion deals with is that some SSIDs will actually generate a few data points and they have to correctly be named after the conversion. So for example `//:class.cpu//:stat.usage//:part.mode(user,kernel,stolen,intr)//:op.rate//:op.util` will partition the CPU usage in `user`, `kernel`, `stolen`, and `intr` (interrupt). The conversion will for example convert this to `cpu_usage_rate_util_user`, `cpu_usage_rate_util_kernel`, `cpu_usage_rate_util_stolen`, and `cpu_usage_rate_util_intr` with all the correct values. 

As the script currently doesn't recognize all these mechanisms it's also somewhat limited in which SSID responses it can parse at this point. For example it currently doesn't fully understand the response coming from `//:part.latency` in `//:class.disk//:stat.io-completions//:part.latency//:op.rate` yet. All the "regular" SSIDs should be fine, just be cautious with the partitioning mechanisms. 

### Export data 

Once the data is converted it can now be exported. The script is intended to allow the export to various tools like InfluxDB, Prometheus, Splunk, and plain text, however this first release can only export the data to a Splunk HTTP Event Collector (HEC). 

The mainly, this function does the formatting of the data specific to the tool it's going to be connecting to, and then does the export. In the case of the Splunk HEC the script connects to the HEC over HTTP, authenticates, and pushes the data. 

## Config files

The Scraper script uses two different YAML configuration files:

* `sstore_list.yaml` — Which holds the list of SSIDs the Scraper script will pull from the StatsStore on each request. The list is currently populated by the SSIDs of some of the main WebUI Sheets. This list can be changed at will to reflect the stats required, do note that, as mentioned above, not all of the StatsStore operators are understood be the converter. 
* `server_info.yaml` — Which hold the configuration of the Scraper itself. It has three sections:
  * `servers:` — Where you indicate where to fetch the data. In the current version it only gathers through the local RAD interface which is indicated with `server_port: "local"`, where `localhost:` is just the server name.
  * `agent:` — Where right now only the interval time is being configured.
  * `destination:` — Where the export function is configured. The  `splunk:` section both defines Splunk as the destination type as well as how to connect to the HEC. The `server_endpoint:`, `request_type:`, `request_transport:`, and `request_uri:` are used to define the HTTP URL. `headers:` holds the HEC authorization key needed to authenticate and select the correct metric the data will go into. and `data_template:` used as the base template for the data that goes to the Splunk HEC.

Any changes to either file will require the service to be restarted.

## SMF Manifest

To ensure the StatsStore Scraper script is always running this example encapsulates an SMF manifest that can be used to create an SMF service for the Scraper script. By enabling this service Oracle Solaris will start the script every time the system boots, as well as if there's an issue with the script and it fails. All the logging information will go to log associated with the SMF service too.

Here's an example of the `svcs -lp` output:

```bash
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

 The SMF manifest XML file can be found at `build/proto_install/lib/svc/manifest/site/sstore_scraper.xml` in this repository.

## IPS Manifest and Package

In addition to using SMF to make it easy to consistently run the Scraper script this example also shows how to bundle up all the files, create an IPS package, and put it in a repository. It can then either be installed over the network or a `p5p` file can be used to install it from file.

The example supplies the `p5m` file that was used to create the example package. The full process normally includes various steps where the the `pkgsend`, `pkgmogrify`, `pkgdepend`, `pkglint`, and `pkgrepo` commands are used to define the meta data, discover the files, and check for things like dependencies. However there is some amount of post-processing need, for example to prune unnecessary entries and tweak certain lines, so we're only supplying the final `p5m` file which can be found at `build/sstore_scraper.p5m.3.res`. This is all that is needed to build your own package if you keep the package contents the same. 

In short to create the package using the files in the `build` directory run the following commands. First create a package repository if you don't already have one:

```bash
# pkgrepo create scraper_repo
# pkgrepo set -s scraper_repo publisher/prefix=scraper
```

Where `scraper_repo` is the name of the directory that will hold the repository. And `publisher/prefix=scraper` defines the name of the IPS publisher that the package will be associated with.

Then create the package in the new repository:

```bash
# pkgsend -s /full/path/to/repository/location/scraper_repo publish -d build/proto_install build/sstore_scraper.p5m.3.res
pkg://scraper/stats/statsstore/sstore_scraper@0.3,5.11:20220921T172649Z
PUBLISHED
```

You can check if it made it in correctly:

```bash
# pkgrepo info -s scraper_repo
PUBLISHER PACKAGES STATUS           UPDATED
scraper   1        online           2022-09-21T11:01:08.746623Z
# pkg info -g /root/scraper_repo sstore_scraper
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

For more details on the full process see [Creating and Publishing a Package](https://docs.oracle.com/cd/E53394_01/html/E54820/pkgcreate.html).

Then you can either set up your own HTTP based server similar to what is described in [How to Enable Users to Retrieve Packages Using an HTTP Interface](https://docs.oracle.com/cd/E37838_01/html/E60982/scalability.html). Example steps:

```bash
# pkg install package/pkg/depot
           Packages to install:  1
            Services to change:  1
       Create boot environment: No
Create backup boot environment: No

Planning linked: 0/1 done; 1 working: zone:test1
Linked image 'zone:test1' output:

Planning linked: 1/1 done
DOWNLOAD                                PKGS         FILES    XFER (MB)   SPEED
Completed                                1/1         17/17      0.0/0.0  268k/s

Downloading linked: 0/1 done; 1 working: zone:test1
Downloading linked: 1/1 done
PHASE                                          ITEMS
Installing new actions                         61/61
Updating package state database                 Done 
Updating package cache                           0/0 
Updating image state                            Done 
Creating fast lookup database                   Done 
Executing linked: 0/1 done; 1 working: zone:test1
Executing linked: 1/1 done
Updating package cache                           3/3
# svccfg -s pkg/server add scraper
# svccfg -s pkg/server:scraper setprop pkg/inst_root=/full/path/to/repository/location/scraper_repo/
# svcadm refresh pkg/server:scraper
# svcadm enable pkg/server:scraper
```

Alternatively you can pull the package into an archive in the form or a `p5p` file:

```bash
# pkgrecv -s /full/path/to/repository/location/scraper_repo_stage/ -a -d sstore_scraper.p5p sstore_scraper
```

This `p5p` file can now be moved to the destination system or put on an NFS share and install directly from it. For steps on how to install the package see the **[Packages folder](../Packages)**.

Copyright (c) 2022 Oracle and/or its affiliates and released under the [Universal Permissive License (UPL)](https://oss.oracle.com/licenses/upl/), Version 1.0