# StatsStore Threshold Alerts

Oracle Solaris 11.4 allows you to set custom FMA alerts and this document walks you through each component involved in the process. Below is a video summarizing all the steps being followed in this demonstration.

![](/Blog_Supplements/Threshold_FMA_Alerts/Screenshots/FMA2.gif)



## Oracle Solaris Dashboard with the Faults, Alerts and Activity dropdown

![](/Blog_Supplements/Threshold_FMA_Alerts/Screenshots/FMA.png)



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

![TestFile Creation](/Blog_Supplements/Threshold_FMA_Alerts/Screenshots/300sec_interval_testfile.png)



Since this file is of 1900m, it causes the operating capacity of the test-zpool to reach a 93% utilization rate, well beyond the optimal 90%. However, since the query time interval is of 300 seconds, for the first alert to kick-in it takes 300 seconds since the creation of the testfile. In our case the file was created at 2:44:49 pm PST and the first alert showed up at 2:49:47 pm PST, after a 5 min interval.

![First Alert](/Blog_Supplements/Threshold_FMA_Alerts/Screenshots/firstalert.png)



The Faults, Alerts and Activity monitor on the Oracle Solaris 11.4 Dashboard, shows us how the alerting system works.

![FMA_Alert](/Blog_Supplements/Threshold_FMA_Alerts/Screenshots/FMA_Alert.png)



![alert_list](/Blog_Supplements/Threshold_FMA_Alerts/Screenshots/alerts_list.png)



However, Oracle Solaris offers you the option to customize the query intervals for a much faster response and alerting system.



### Case (2): With check time interval as 60 seconds

For this piece of the simulation, we modify our query time to 60 seconds and update the `zpool-usage.json` file in the `/usr/lib/sstore/metadata/json/thresholds` directory, as discussed above. With the query time interval, now set to 60 seconds, alerts kick-in faster and we can act to resolve the error.

Here is how we create testfile, testfile1 and testfile 2 to simulate a compounding increase in the test zpool storage.

![test-file2](/Blog_Supplements/Threshold_FMA_Alerts/Screenshots/testfile2.png)

Since the net storage utilization is of 1860m, it causes the operating capacity of the test-zpool to reach a 93% utilization rate, well beyond the optimal 90%. However, since the query time interval is now of 60 seconds, the first alert to kicks-in faster since the creation of the testfile. In this case though we analyze, for how long after the deletion of the additional file, does the WebUI show a first reduction in the storage utilization. After the testfile2 has been deleted from the test-zpool the stat, the WebUI shows us the first drop in less than 120 seconds (>300 seconds), thus  making sure the alerting system works faster with a 60 second query interval.

![test-file2](/Blog_Supplements/Threshold_FMA_Alerts/Screenshots/threshold_alert.png)



## Using the Command Line Interface to observe these changes	

The Oracle Solaris WebUI and the FMA alerting system makes use of the sstore and ssid (stats store identifier) in order to represent the threshold values on the graph. These values can be monitored using the:`//:class.zpool//:res.name/test-zpool//: > capture stat.capacity` which captures the data in the following format:

```
2020-11-12T15:19:43 93 //:class.zpool//:res.name/test-zpool//:stat.capacity
2020-11-12T15:19:44 93 //:class.zpool//:res.name/test-zpool//:stat.capacity
2020-11-12T15:19:45 93 //:class.zpool//:res.name/test-zpool//:stat.capacity
2020-11-12T15:19:46 93 //:class.zpool//:res.name/test-zpool//:stat.capacity
2020-11-12T15:19:47 88 //:class.zpool//:res.name/test-zpool//:stat.capacity
c2020-11-12T15:19:48 88 //:class.zpool//:res.name/test-zpool//:stat.capacity
2020-11-12T15:19:49 88 //:class.zpool//:res.name/test-zpool//:stat.capacity
```



In order to create more custom threshold limits, please refer to the [ssid-metadata(7)](https://docs.oracle.com/cd/E88353_01/html/E37853/ssid-metadata-7.html) documentation.

Blog about StatsStore threshold alerts, [here](https://blogs.oracle.com/solaris/statsstore-threshold-alerts-v2).







 Copyright (c) 2020, Oracle and/or its affiliates. Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.











