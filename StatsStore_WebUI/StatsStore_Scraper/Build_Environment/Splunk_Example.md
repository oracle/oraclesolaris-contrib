# The Splunk Example

In this Splunk example the StatsStore Scraper script runs on each Oracle Solaris instance that you want to pull data from. The script is installed through a package and because the package comes with and SMF manifest, which makes it an SMF service that can be turned on. This means that SMF will also automatically start it after a reboot or if the script hits an issue. The only thing that needs to be done before the SMF service is enabled is to configure where the script can find the Splunk HTTP Event Collector (HEC) and give it the correct credentials to do so.

## Getting started

There are three ways to get the StatsStore Scraper script installed and running. 

* Build the IPS package yourself — The steps for this are explained in the **IPS Manifest and Package** section of the **[StatsStore Scraper structure](./StatsStore_Scraper_Structure.md)** document. The benefit of this approach is that you can choose to incorporate changes into the package before building it and this way customize it for your use.
* If you rather just use the package we built go to the **[Packages](../Packages)** directory and pickup the pre-built package from there.
* Take the Scraper script and just run it as is on its own — I could be that you just want to talk the script, copy it somewhere and run it there without the use of the package and SMF. 

If you're going for one of the first two options you'll want to install the package, configure the `server_info.yaml` file, and start the service. The details on this are also in the **[Packages](../Packages)** directory. 



## The structure

The structure of the package is fairly simple. 

* The working directory is in `/opt/sstore_scraper`, where `/opt/sstore_scraper/bin` holds the Python code, and `/opt/sstore_scraper/etc` holds the config files. For more details on these files see the **Config files** section of the **[StatsStore Scraper structure](./StatsStore_Scraper_Structure.md)** document.

* The SMF manifest is placed in `/lib/svc/manifest/site`, where it can be imported by SMF. The actual import is triggered by `restart_fmri=svc:/system/manifest-import:default` in the package manifest. 

  Once installed the SMF service is intentionally disabled to allow configuration before it is enabled. If you were to choose to embed all the necessary config data in a self-built package you could choose to have the service automatically enabled. This can be done by changing `<instance name="default" enabled="false"/>` to `<instance name="default" enabled="true"/>` in the SMF manifest file `sstore_scraper.xml`.

That's pretty much it.

Note that this script only pushes data into Splunk we don't have any examples on how to create Dashboards in Splunk. This is out of scope of this example.

## Requirements

The requirements are slightly loose. Of course this will have to run on Oracle Solaris 11.4 as this is the only version that has the StatsStore. The other thing is that the script is written in Python 3, tested on systems where this is Python 3.7. 

Also note this was tested on systems SRU 36 and higher, as we moved from Python 2.7 being the default to Python 3.x being the default early SRUs probably won't have all the Python 3.7 packages installed that are needed. 

There are a few requirements on Python modules and it may be the case they are not installed with the group package installed on the system. Specifically, the `pyyaml` package as may be missing. Therefore we've added a dependency in the IPS manifest (`sstore_scraper.p5m.3.res`) to install this package incase it's not installed already. If you choose to edit the script and add extra modules check if they are installed in the group packages you use or add their dependency to the IPS manifest too.

The Splunk version this was tested is 8.2.3, but seeing that the HEC interface is stable this should work with a wide variety of Splunk versions.

## Versions

* v0.3 — The initial release. 

  This version is installed on the source host and connects out to a single Splunk HEC. It can understand and simplify a large amount but not all the StatsStore SSIDs. It is delivered with an SMF manifest and a way to deliver it through an IPS package. This makes install easy and once configured SMF will restart the service on an outage.

  * Known elements still missing:
    * Python exception handling of Splunk connection errors — It currently doesn't cleanly deal with all the possible connection issues.
    * Check for Splunk config — It doesn't check if the `server_info.yaml` config file is not edited after the default install.
    * Signing the package — How to sign the package hasn't been added yet.
    * More StatsStore SSIDs to choose from in config file — The list of SSIDs in the `sstore_list.yaml` file isn't complete. That is to say it doesn't have all the SSIDs available in the WebUI Sheets yet.
    * Support for more SSID types — Not all the SSID operations are understood how to parse the output yet by the script. Currently it understands how to parse a single data field, a `REAL`, and an answer containing a `DICTIONARY`, where there are multiple answers for a single SSID. For example when using a `part.mode`. 

Copyright (c) 2022 Oracle and/or its affiliates and released under the [Universal Permissive License (UPL)](https://oss.oracle.com/licenses/upl/), Version 1.0