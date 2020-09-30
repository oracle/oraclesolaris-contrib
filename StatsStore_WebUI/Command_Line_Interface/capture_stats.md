# Extracting data from StatsStore using the Command Line Interface

## Capturing the timestamp across which to capture data

Time stamps in Oracle Solaris are based off the [`date(1)`](https://docs.oracle.com/cd/E88353_01/html/E37839/date-1.html) utility. It writes the date and time to standard output or attempts to set the system date and time. By default, the current date and time is written.

```
date +%y-%m-%d:%H:%M
```

For example:

```
20-05-21:13:49
```

If the start time and end time of the period is known/planned, you can jump directly to Step (1).

### If the timestamp is unknown/ you want to observe the statistics first:

**Utilizing CLI to capture floating point utilization and corresponding time stamps:**

If interacting directly with the StatsStore, you can type in the following command to jump directly to capturing the data across the appropriate timestamps:

```
~/solarisdemobox$ sstore capture //:class.cpu//:stat.fpu-usage
```

The output of using the above command is:

```
TIME                VALUE IDENTIFIER
2020-05-13T14:47:20 61227515078.0 //:class.cpu//:stat.fpu-usage
2020-05-13T14:47:21 61227798478.0 //:class.cpu//:stat.fpu-usage
2020-05-13T14:47:22 61228007625.0 //:class.cpu//:stat.fpu-usage
2020-05-13T14:47:23 61228463341.0 //:class.cpu//:stat.fpu-usage
2020-05-13T14:47:24 61228503642.0 //:class.cpu//:stat.fpu-usage
2020-05-13T14:47:25 61228543981.0 //:class.cpu//:stat.fpu-usage
```



## Step (1): Exporting data to a file

#### Now, if as a user you want to retrieve data from a specific statistic:

If you use the Properties dropdown on the Oracle Solaris Analytics Dashboard, you can directly access the SSID for the statistic you wish to download. The standard code placeholder for retrieving has to be followed by:

```
//:class.<Place your class title here>//:stat.<Place the stat name here>
```

As an example, we are building this document using:

```
 //:class.cpu//:stat.fpu-usage
```



#### Exporting the data about floating point utilization:

The standard command template to export data is as follows:

```
~/solarisdemobox$ sstore export -t <Start Timestamp> -e <End Timestamp> -i <Step Count> //:class.<Place your class title here>//:stat.<Place the stat name here>
```

##### a*) Creating a file*

In order to create a file first:

```
~/solarisdemobox$ touch myfpu-util
```

##### *b) Exporting the data to a file*

In order to export data to this file in the directory:

```
~/solarisdemobox$ sstore export -t 2020-05-13T14:47:20 -e 2020-05-13T14:47:25 -i 1  //:class.cpu//:stat.fpu-usage > myfpu-util
```

The contents of myfpu-util:

```
TIME                VALUE IDENTIFIER
2020-05-13T14:47:20 61227515078.0 //:class.cpu//:stat.fpu-usage
2020-05-13T14:47:21 61227515078.0 //:class.cpu//:stat.fpu-usage
2020-05-13T14:47:22 61227798478.0 //:class.cpu//:stat.fpu-usage
2020-05-13T14:47:23 61228007625.0 //:class.cpu//:stat.fpu-usage
2020-05-13T14:47:24 61228463341.0 //:class.cpu//:stat.fpu-usage
2020-05-13T14:47:25 61228503642.0 //:class.cpu//:stat.fpu-usage
```



## Step (2): Exporting the data in a csv format

The standard command template to export data is as follows:

```
~/solarisdemobox$ sstore export -F csv -t <Start Timestamp> -e <End Timestamp> -i <Step Count> //:class.<Place your class title here>//:stat.<Place the stat name here> 
```

##### a) Creating a file

```
~/solarisdemobox$ touch myfpu-util.csv
```

##### b) Exporting the data to a file

```
~/solarisdemobox$ sstore export -t 2020-05-13T14:47:20 -e 2020-05-13T14:47:25 -i 1  //:class.cpu//:stat.fpu-usage > myfpu-util.csv
```

The contents of `myfpu-util.csv`:

```
time,//:class.cpu//:stat.fpu-usage
1589406440000000,61227515078.000000
1589406441000000,61227515078.000000
1589406442000000,61227798478.000000
1589406443000000,61228007625.000000
1589406444000000,61228463341.000000
1589406445000000,61228503642.000000
```


Copyright (c) 2020, Oracle and/or its affiliates.
 Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.
