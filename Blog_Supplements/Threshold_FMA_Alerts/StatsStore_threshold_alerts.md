# StatsStore Threshold Alerts

The Oracle Solaris Fault Management feature provides an architecture for building resilient error handlers, structured error telemetry, automated diagnostic software, response agents, and structured messaging. Many parts of the software stack participate in Fault Management, including the CPU, memory and I/O subsystems, Oracle Solaris ZFS, an increasing set of device drivers, and other management stacks. The Oracle Solaris Analytics dashboard enables users to monitor these Faults and Alerts both using the WebUI alerting pop-up as well as the graphical representations.

This markdown document simulates an overload in ZFS pool capacity and walks you through the various pieces involved in setting threshold alerts and monitoring the results.

![](Screenshots\FMA.png)

## Analyzing the threshold alerts for  ZFS Pool Capacity

The ZFS Pool Capacity (%) helps to understand the percentage of pool space utilized by zpools. To ensure optimal performance of the ZFS file storage system, this percent utilization should be well below 90%. In order to monitor this threshold utilization by zpool resources, the FMA alert makes use of the `zpool-usage.json` file in the `/usr/lib/sstore/metadata/json/thresholds` directory. The `zpool-usage.json` file looks something like this:

```json
{
    "$schema": "//:threshold",
    "copyright": "Copyright (c) 2019, Oracle and/or its affiliates. All rights reserved.",
    "description": "Default threshold mapping for zpool usage",
    "id": "zpool-usage",
    "query-interval": 10,
    "ssid-threshold-map-list": [
        {
            "ssid": "//:class.zpool//:*//:stat.capacity",
            "ssid-query-interval": 300,
            "ssid-threshold-list": [
                "90.0"
            ]
        }
    ]
}
```

To learn more about the `zpoolusage.json` and other associated `.json` that can be used to set thresholds limits for the FMA alerts, please refer to [ssid-metadata(7)](https://docs.oracle.com/cd/E88353_01/html/E37853/ssid-metadata-7.html) page.

## Modifying the `zpool-usage.json` for custom thresholds and alerts

The standard `zpool-usage.json` file has been based off the Threshold mapping parameters as explained below:

```
ssid-threshold-map-list
```

The `ssid-threshold-map-list` member is a list of `ssid-maps` consisting of `ssid` and `ssid-threshold-list`.

```
ssid-threshold-list
```

The `ssid-threshold-list` member is a list of strings representing floating point numbers. A negative threshold value represents a lower threshold which means the stat is checked for lower than the absolute value of the threshold. A positive threshold value represents a higher threshold which means the stat is checked for higher than the given threshold value.

```
ssid-query-interval
```

If required, you can specify `ssid-query-interval`. This defines the time interval between threshold checks for the `ssid`. The default value for `ssid-query-interval` is 10 seconds.

```
query-interval
```

If required, you can specify `query-interval` which defines the minimum time interval for threshold checks applicable for all the ssid's in `ssid-threshold-map-list`. The default value for `query-interval` is 10 seconds.

```json
{
    "$schema": "//:threshold",
    "copyright": "Copyright (c) 2019, Oracle and/or its affiliates. All rights reserved.",
    "description": "Default threshold mapping for zpool usage",
    "id": "zpool-usage",
    "query-interval": 10,  //Default ssid query interval
    "ssid-threshold-map-list": [
        {
            "ssid": "//:class.zpool//:*//:stat.capacity",
            "ssid-query-interval": 300,  //Defined threshold check time interval(300 seconds=5 minutes)
            "ssid-threshold-list": [
                "90.0" //sstore threshold limit
            ]
        }
    ]
}
```

### Modifying the zpool-usage.json file for our simulation

For our simulation, I will be changing the threshold check time interval to 60 seconds, while keeping all other parameters intact to get any changes in threshold values faster.

```json
{
    "$schema": "//:threshold",
    "copyright": "Copyright (c) 2019, Oracle and/or its affiliates. All rights reserved.",
    "description": "Default threshold mapping for zpool usage",
    "id": "zpool-usage",
    "query-interval": 10,  
    "ssid-threshold-map-list": [
        {
            "ssid": "//:class.zpool//:*//:stat.capacity",
            "ssid-query-interval": 60,  
            "ssid-threshold-list": [
                "90.0" 
            ]
        }
    ]
}
```

Now the system returns the percent utilization values at each minute to ensure if there are sudden increments, the user knows about them.



## Analyzing the threshold limits for a simulated workload increase

### Case (1): With check time interval as 300 seconds

With the default time-interval set to 300 seconds in the `zpool-usage.json` file, the system checks for threshold limits every 300 seconds or 5 minutes. In our case, we have our test-zpool with a storage capacity of 1.98 GB and we create a testfile in this test-zpool of 1900MB.

![TestFile Creation](Screenshot/300sec_interval_testfile.png)



Since this file is of 1900m, it causes the operating capacity of the test-zpool to reach a 93% utilization rate, well beyond the optimal 90%. However, since the query time interval is of 300 seconds, for the first alert to kick-in it takes 300 seconds since the creation of the testfile. In our case the file was created at 2:44:49 pm PST and the first alert showed up at 2:49:47 pm PST, after a 5 min interval.

![First Alert](Screenshot/firstalert.png)



The Faults, Alerts and Activity monitor on the Oracle Solaris 11.4 Dashboard, shows us how the alerting system works.

![FMA_Alert](Screenshot/FMA_Alert.png)



![Alert_List] (Screenshot/alerts_list.png)





