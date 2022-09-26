# The Build Environment

The build environment directory holds both the example code as well as the extra information on how the StatsStore Scraper works and how to use it. Additionally it holds the information on how to for example create an SMF service and an IPS package if this is relevant for you.

The structure of how the StatsStore Scraper code works can be found in the [StatsStore Scraper structure document](StatsStore_Scraper_Structure.md).

Currently there is only one example use case which allows the StatsStore Scraper to push data into Splunk. In this case the StatsStore Scraper is installed as a package and SMF service. This is done on the source system which means it will use the internal RAD interface to pull data from the StatsStore. More details on this example can be found in the [Splunk example document](Splunk_Example.md).

Copyright (c) 2022 Oracle and/or its affiliates and released under the [Universal Permissive License (UPL)](https://oss.oracle.com/licenses/upl/), Version 1.0