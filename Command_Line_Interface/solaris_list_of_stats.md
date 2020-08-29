# List of available stats from the StatsStore

The StatsStore (`sstore`) contains a list of important statistics and parameters which can help you understand system performance, event specific data points, resource allocations as well as key information regarding zones.

The stats from Oracle Solaris 11.4 are classified as per [Classes](https://docs.oracle.com/cd/E37838_01/html/E56520/ssids.html#SSTORssidstructure).

To understand all the types of classes and statistics available in Oracle Solaris 11.4, use the following command in CLI:

```
~/solarisdiscover$ sstore
Interactive mode. Type help to see list of commands.
//: > ls
```

To further understand the types of statistics available , we have classified them as follows:

| Class Name | Description                | Corresponding Stats                                          |
| ---------- | -------------------------- | ------------------------------------------------------------ |
| app        | Application                | class.app/oracle/rdbms<br />class.app/solaris/apache<br />class.app/solaris/audit/class <br />class.app/solaris/compliance/assessment<br />class.app/solaris/compliance/rule<br />class.app/solaris/install/auto-install<br />class.app/solaris/nscd<br />class.app/solaris/sstore<br />class.app/solaris/sysstat/sysconf |
| collection | StatsStore Collections     | class.collection |
| cpu        | Processor                  | class.chip<br />class.core<br />class.cpu<br />class.dax<br />class.lgroup<br />class.pset<br />class.scheduler |
| dev        | Devices                    | class.dev<br />class.devices |
| ib         | Infiniband IO              | class.ib/hca<br />class.ib/hca-phys<br />class.ib/ulp |
| networking | Network IO                 | class.link<br />class.link/phys<br />class.net/flow<br />class.net/ip<br />class.net/tcp<br />class.net/udp |
| pg         | Processor Group Statistics | class.pg/CPU-PM-Active-Power-Domain<br />class.pg/CPU-PM-Idle-Power-Domain<br />class.pg/Cache<br />class.pg/Data-Pipe-to-memory<br />class.pg/Floating-Point-Unit<br />class.pg/Integer-Pipeline<br />class.pg/L2-Cache<br />class.pg/L3-Cache<br />class.pg/Socket<br /> |
| process    | Per Process Statistics     | class.proc                                                   |
| storage    | Storage                    | class.disk<br />class.disk-controller<br />class.fs<br/>class.fsflush<br />class.fstype<br />class.nfs/client<br />class.nfs/server<br />class.pageout<br />class.zpool |
| svc        | Services and Events        | class.svc<br />class.event                                   |
| system     | System                     | class.system                                                 |

For more information regarding classes and statistics available with Oracle Solaris 11.4, please refer to the link below:

- [Statistics Store Identifiers](https://docs.oracle.com/cd/E37838_01/html/E56520/ssids.html#SSTORssidstructure)
- [Using the Command Line Interface](https://docs.oracle.com/cd/E37838_01/html/E56520/sstorconsume.html#scrolltoc)

Copyright (c) 2020, Oracle and/or its affiliates.
 Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.
