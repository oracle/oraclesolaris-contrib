# StatsStore Scraper

Using the Oracle Solaris RAD/REST interface it is possible to connect to the Oracle Solaris StatsStore and export data it is currently gathering or has gathered in the past. This can be done remotely through the RAD/REST external interface or locally on the system using the internal RAD interface and then export this to some external data store like a time-series database. This section plans shows various ways how to do this with a script—or more precicely a set of scripts—that we're calling the StatsStore Scraper. These scripts are witten in Python and should run on new versions of Oracle Solaris 11.4.

**Note:** The StatsStore Scraper script is not supported as part of Oracle Solaris and falls under the [Universal Permissive License (UPL)](https://oss.oracle.com/licenses/upl/). It is purely intended to help Oracle Solaris administrators on gathering data from the StatsStore by showing how this can be done. 

## Main architecture

The StatsStore Scraper has three main parts:

1. Connection to StatsStore to pull data
2. Transformation/simplification of the data
3. Exporting the data

### Connection to StatsStore to pull data

When connecting to the StatsStore this can either be done remotely from another system over the RAD/REST interface or locally within the Oracle Solaris instance over RAD. There are various pro's and con's in these to approaches, the main ones are:

**Remote**

| Pro's                                           | Con's                                                     |
| ----------------------------------------------- | --------------------------------------------------------- |
| Multiple Systems from a single collection point | Need to open external port                                |
| No local agent to install and confgiure         | Need to administer connection credentials for new servers |

**Local**

| Pro's                                                       | Con's                                                 |
| ----------------------------------------------------------- | ----------------------------------------------------- |
| No need for an external port to be opened                   | Need to add and configure a local agent or service    |
| No extra work when adding new servers outside these servers | Administration is now spread out over all the systems |

The StatsStore Scraper has the capability to do both but the first version will only use the local RAD connection to pull data from.

### Transformation/simplification of the data

When using the RAD/REST interface the way to communicate data is through JSON datagrams. The JSON data going in mostly contains the names of the StatsStore stats—called StatsStore IDs or SSIDs—you want to gather and for which time period you want to retrieve these stats. The data coming out is a JSON datagram mostly containing the resulting information on the SSIDs that were requested. One of the main challenges with exporting this data into an external store is that the JSON pretty nested and is currently not very easy to pass on without some amount of conversion. 

Here is a simple example of what the resulting JSON datagram looks like:

```json
{"payload": {"formatted_records": null,
             "records": [{"points": [{"point_range": null,
                                      "point_type": "VALUE_POINT",
                                      "point_value": {"ts": 1638346115174970,
                                                      "value": {"boolean_val": false,
                                                                "dictionary": null,
                                                                "dictionary_array": null,
                                                                "number": 0,
                                                                "number_array": null,
                                                                "real": 299887.0,
                                                                "real_array": null,
                                                                "string": null,
                                                                "string_array": null,
                                                                "type": "REAL"}}}],
                          "ssid": "//:class.cpu//:stat.fpu-usage//:op.rate"}],
             "warnings": []},
"status": "success"}
```

And this is what you'd want it to look like to easily import it into a regular time-series database:

```
cpu.fpu-usage.rate=299887.0 1638346115174970
```

Where the SSID/name has been greatly simplified from `//:class.cpu//:stat.fpu-usage//:op.rate` to `cpu.fpu-usage.rate`, followed by the value, followed by the timestamp of the data. Of course you can reorder this depending on which tool you'll be exporting this to, this example was for InfluxDB, but you could for example change it to something like this:

```
metric_name:cpu.fpu-usage.rate: 299887.0
```

Or:

```
cpu.fpu-usage.rate,299887.0,1638346115174970
```

What ever you need, but the base simplification task remains the same.

### Exporting the data

Once the data has been pulled from the StatsStore and it is transformed it can now be exported to a 3rd party tool like InfluxDB, Prometheus, or Splunk. How this is done is mostly up to the tool being used. For example in the cases of InfluxDB and Splunk the scraper script will need to push the data out to it, where for example Prometheus prefers to pull the data from a webpage formatted in a certain way. This means that this step will be greatly dependent on your favorite tool and how it ingests data. Often the tools are fairly flexible and sometimes can ingest formats from other well known tools or have something to transform it.

## Examples

The first example we're publishing is a version of the StatsStore Scraper that can push data into Splunk by pushing data into the [HTTP Event Collector](https://docs.splunk.com/Documentation/Splunk/9.0.1/Data/UsetheHTTPEventCollector). In this case the StatsStore Scraper runs inside the Oracle Solaris instance where it connects to the StatsStore through the local RAD instance. 

![Example Sheet](/StatsStore_WebUI/Images/StatsStore_Scraper/Splunk_Screenshot.png)

To connect the the Splunk HEC you'll need to have the correct credentials to push data to it which you can get through the Splunk interface. These credentials are then embedded in the REST header which the StatsStore Scraper uses to talk to the Splunk HEC. The credentials have two functions, the first is to validate that the data should be accepted in by the HEC and second, which metric in Splunk this data should be associated with. The HEC can ingest multiple metrics each with their own credentials. So you could choose to have different server groups push into different metrics.

Because the StatsStore Scraper is running inside the Oracle Solaris instance the added bonus is that we can create an SMF service for it and create an IPS package for it so it can be rolled out by installing the package and then configured. If all the Oracle Solaris instances are pointing to the same Splunk HEC and metric you could even embed the Splunk keys in the configuration and install them as part of the install. Alternatively you could use something like Puppet or Ansible to do the configuration.

We're supplying both the StatsStore Scraper code as well as a prebuilt package. For more details on the actual code check out the [build environment](Build_Environment) and if you just want to use the pre-built package you can go the [packages](Packages).

Copyright (c) 2022 Oracle and/or its affiliates and released under the [Universal Permissive License (UPL)](https://oss.oracle.com/licenses/upl/), Version 1.0