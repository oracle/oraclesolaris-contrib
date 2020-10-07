# Sample Sheet with detailed statistics	

The StatsStore (`sstore`) contains a list of important statistics and parameters and the sample sheet attached below focusses on some detailed stats from the list below.

Link: [Sample Sheet](/StatsStore_WebUI/Sharing_Sheets/solaris-contrib.json)

![Sample Sheet with basic statistics](/StatsStore_WebUI/Images/Sharing_Sheets/solaris-contrib.png)

To further understand the types of statistics available , we have classified them as follows:

| Class Name | Description            | Corresponding Stats                                          | Statistics                                                   |
| ---------- | ---------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| app        | Application            | class.app/solaris/audit/class<br />class.app/solaris/sstore<br /> | sstat.events//:part.long-classname(file-close,file-attr-access,file-create,file-delete,file-attr-modify,file-read)<br />stat.events//:part.long-classname(proc-modify,proc-start-stop,ioctl,ipc,network,application)<br />stat.events//:part.long-classname(sys-admin,login-logout,priv-exec,chg-sys-state,user-admin,x-srv-access<br />stat.repo-size<br />stat.repo-size<br />s.[dynamic-enabled,dynamic-disabled]<br />s.[persistent-enabled,persistent-disabled]<br />s.[namespace-size,stats-removed]<br />s.[door-threads-created,door-threads-deleted]<br />s.[worker-threads-created,worker-threads-deleted]<br />stat.data-returned<br />stat.response-cache-hits<br /> |
| networking | Network IO             | class.link<br />class.link/phys<br />                        | stat.in-bcast-bytes<br/>stat.in-bcast-packets<br/>stat.in-bytes<br/>stat.in-drop-bytes<br/>stat.in-drops<br/>stat.in-mcast-bytes<br/>stat.in-mcast-packets<br/>stat.in-packets<br/>stat.out-bcast-bytes<br/>stat.out-bcast-packets<br/>stat.out-bytes<br/>stat.out-drop-bytes<br/>stat.out-drops<br/>stat.out-mcast-bytes<br/>stat.out-mcast-packets<br/>stat.out-packets |
| process    | Per Process Statistics | class.proc                                                   | stat.memory-percentage                                       |



Copyright (c) 2020, Oracle and/or its affiliates.
 Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.