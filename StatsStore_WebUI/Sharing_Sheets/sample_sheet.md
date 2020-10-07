# Sample Sheet with some basic statistics

The StatsStore (`sstore`) contains a list of important statistics and parameters and the sample sheet attached below focusses on some basic stats from the list below.

Link: [Sample Sheet]/StatsStore_WebUI/Sharing_Sheets/sample-sheet.json)

![Sample Sheet with basic statistics](/StatsStore_WebUI/Images/Sharing_Sheets/sample-sheet.png)

| Class Name | Description | Corresponding Stats                                          | Statistic                                                    |
| ---------- | ----------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| cpu        | Processor   | class.chip<br />class.core<br />class.cpu<br />class.dax<br />class.lgroup<br />class.pset<br />class.scheduler | stat.usage<br /> stat.fpu-usage<br />stat.integer-pipe-usage<br /> |
| networking | Network IO  | class.link<br />class.net/ip<br />class.net/tcp              | stat.in-bytes<br />stat.out-bytes<br />stat.in-bytes<br />stat.out-bytes<br />stat.in-data-inorder-bytes<br />stat.out-data-bytes |
| storage    | Storage     | class.disk<br />class.fs<br/>                                | stat.run-time<br />stat.read-bytes<br />stat.write-bytes<br />s.[read-bytes,write-bytes]<br />s.[read-ops,write-ops] |
| system     | System      | class.system                                                 | stat.load-average                                            |



- Copyright (c) 2020, Oracle and/or its affiliates.
   Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.
