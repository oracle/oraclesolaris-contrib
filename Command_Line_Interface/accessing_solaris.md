## Accessing Oracle Solaris 11.4 and the StatsStore

Before we start discussing building custom templates for sheets, a quick detour to cover the basics:

### 1) Logging into Oracle Solaris 11.4 using CLI

Using command line interfaces (Terminal for MacOS and Putty for Windows), you can remotely login to Oracle Solaris via SSH. Once in the CLI, you must have a username and password to start a new session on Oracle Solaris.

```
login as: demo
Keyboard-interactive authentication prompts from server:
 Password:`
End of keyboard-interactive prompts from server
Last login: Thu May 21 09:00:49 2020 from 10.xxx.xx.xx
Oracle Corporation      SunOS 5.11      11.4    July 2019
You have mail.
~/solarisdiscover$
```

### 2) Syntax for time-stamps

Time stamps in Oracle Solaris are based off the  `date` utility. It writes the date and time to standard output or attempts to set the system date and time. By default, the current date and time is written.

```
date +%y-%m-%d:%H:%M
```

Output:

*20-05-21:13:49*

For more information on date and time in Oracle Solaris 11.4, click [here](https://docs.oracle.com/cd/E86824_01/html/E54763/date-1.html#REFMAN1date-1)


### 3) Accessing the StatsStore to understand the list of available stats

Once an user logs in to the system, the steps to access the StatsStore are as follows:

```
~/solarisdiscover$ sstore
Interactive mode. Type help to see list of commands.
//: > ls
```

For more information on the list of statistics available on the StatsStore, click [here](https://docs.oracle.com/cd/E37838_01/html/E56520/ssids.html#SSTORssidstructure) or to [this overview list](solarislistofstats.md).	


### 4) Commands to capture and export data

Oracle Solaris 11.4 consists or 2 main commands : `capture` and `export`. Users can only perform analysis on the data that has been captured across a specific timeframe. So either the system has automatically captured the data because of a collection that is turned on, or the capture is forced by either using the WebUI or the `capture` command via the CLI.



For more information; click [here](https://docs.oracle.com/cd/E37838_01/html/E56520/adminanalytics.html)

Copyright (c) 2020, Oracle and/or its affiliates.
 Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.
