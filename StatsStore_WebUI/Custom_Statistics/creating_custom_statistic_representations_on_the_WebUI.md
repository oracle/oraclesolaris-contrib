# Creating custom statistic representations on the WebUI

## Introduction:

The Oracle Solaris Analytics Dashboard offers a variety of default sheets with ready to use visualizations of the most essential statistics for you to monitor system parameters and performance. Apart from these, the Oracle Solaris WebUI also enables you to tap into the `sstore` to create your own version of a sheet, with custom combinations of statistics, events and resource apart from system defaults. This feature enables you to drill down and partition the graphs, as per your specific use-case and save it as a custom sheet to be shared with other users/machines. 

You can find more about sharing a sheet here: [Add a shared sheet](/master/StatsStore_WebUI/Sharing_Sheets/add_shared_sheet.md)

To learn more about a list of statistics available on the `sstore`: [Solaris List of Stats](/master/StatsStore_WebUI/Command_Line_Interface/solaris_list_of_stats.md)

## How to create a new visualization on the WebUI:

![Custom Stats](/StatsStore_WebUI/Custom_Statistics/Images/custom-statistics.png)

After you login to the WebUI, you can either choose to create a new sheet or add a new visualization to an existing sheet created by you. To learn more about creating sheets on the WebUI, [go here](/StatsStore_WebUI/Creating_Sheets/creating_sheets.md).

#### Step 1: Create a new group

![Add Group](/StatsStore_WebUI/Custom_Statistics/Images/add-group.png)



#### Step 2: Adding visualization

![Add Visualization](/StatsStore_WebUI/Custom_Statistics/Images/add-visualization.png)



#### Step 3: Adding a statistic or event

##### Step i: Add a statistic

![Add Statistic](/StatsStore_WebUI/Custom_Statistics/Images/add-statistic.png)

##### Step ii: Enter a new statistic

![Visualization](/StatsStore_WebUI/Custom_Statistics/Images/enter-new-statistic.png)



#### Step 4: Configuring the statistic or event

##### 	Step i: List of elements 

​	![Element List](/StatsStore_WebUI/Custom_Statistics/Images/element-list.png)

##### 	Step ii: List of available classes

​	![Element List](/StatsStore_WebUI/Custom_Statistics/Images/list-of-class.png)

##### 	Step iii: Example partitioning CPU Usage by zones

​	![CPU Usage by Zone](/StatsStore_WebUI/Custom_Statistics/Images/cpu-usage-zone.png)

##### 	Step iv: Example partitioning CPU Usage by core

​	![CPU Usage by Core](/StatsStore_WebUI/Custom_Statistics/Images/cpu-partition-core.png)

#### Step 5: Visualizing the result

![Visualization](/StatsStore_WebUI/Custom_Statistics/Images/cpu-across-zones.png)







Using the steps above, you can create your own combination of statistics and share them with the community here.



Copyright (c) 2020, Oracle and/or its affiliates.
 Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.