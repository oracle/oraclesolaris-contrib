## Live storage migration for Solaris Kernel Zones in a single step

While we have supported Kernel Zone (KZ) live storage migration for a long time, I believe since Solaris 11.2 released in 2014, it has been always a manual multi-step task involving live reconfiguring the KZ to add new devices via [zonecfg(8)](https://docs.oracle.com/cd/E88353_01/html/E72487/zonecfg-8.html), attaching/detaching disks to/from the root zpool via [zpool(8)](https://docs.oracle.com/cd/E88353_01/html/E72487/zoneadm-8.html) executed from within the KZ, and after storage resilvering, reconfiguring the KZ to remove original disk devices via zonecfg(8) again; all that while tracking individual disk IDs across all the steps. If anything failed during the transition, a non-trivial manual clean-up was required.

If a customer had tens or hundreds of Kernel Zones running and needed their storage to migrate, such a process was quite time consuming and error prone.

The Solaris Zones team is pleased to say that from [Oracle Solaris SRU48](https://blogs.oracle.com/solaris/post/announcing-oracle-solaris-114-sru48) released in August 2022, this operation is now fully integrated into the zones framework, and requires a single step to do. It also includes rollback code to revert the state of the Kernel Zone to its original condition if anything goes wrong during the storage migration.



### The zoneadm move command interface

There already was `zoneadm move` command to cold migrate storage for installed [solaris(7)](https://docs.oracle.com/cd/E88353_01/html/E37853/solaris-7.html) and [solaris10(7)](https://docs.oracle.com/cd/E88353_01/html/E37853/solaris10-7.html) branded zones, and we use the same `move` subcommand for the [Kernel Zone brand](https://docs.oracle.com/cd/E88353_01/html/E37853/solaris-kz-7.html).

The interface for Kernel Zones is as follows:

```
zoneadm -z <zone> move -p <URI> [-p <URI> ...] [-v] [-x force-zpool-attach]
```

The storage URIs are those supported by [suri(7)](https://docs.oracle.com/cd/E88353_01/html/E37853/suri-7.html). Presently we support ZFS volumes, iSCSI, Fibre Channel and SAS, and also regular files and files over NFS.

The new extended option `-x force-zpool-attach` is introduced to forcefully attach disk(s) recognized by zpool(8) as having parts of already existing zpools. If not specified, a temporary zpool is tried to get created out of the devices identified by the `-p` options and if such `zpool create` fails, the whole storage migration fails.

New disks are added to the zone configuration with the `bootpri` device property that equals the highest priority from all original disks that are part of the root zpool.

A verbose progress log is always printed to a log located in `/var/log/zone`. Each invocation has its specific log filename (as `attach`, `install`, or `clone` operations do). Name of the log is printed as part of the command line output. The `-v` option makes `zoneadm(8)` print the verbose output also to the terminal.



### Examples

This example shows the default output for migrating a single disk zpool to another disk:

```
root# zoneadm -z lsm move \
    -p iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25F0E0006
Progress being logged to /var/log/zones/zoneadm.20220117T114644Z.lsm.move
Attaching new disks.
Waiting for disks to resilver.
Removing original disks from zone 'lsm' configuration.
Live storage migration succeeded.
```

The new feature is also described in detail in the updated `zoneadm(8)` manual page shipped with the system (the updated version is not online as of publishing this blog post).

The following example shows a verbose output when a single disk zpool is migrated to a two disk mirror. The `-x force-zpool-attach` was only used because I used those two disks already in another zpool tests. Note those resilvering progress log messages providing the estimated time of the job being done:

```
root# zoneadm -z lsm move -v -x force-zpool-attach \
    -p iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25DFC0002 \
    -p iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25E590004
Verbose progress output to terminal enabled.
==== Starting:  ====
Progress being logged to /var/log/zones/zoneadm.20220718T003054Z.lsm.move
Verifying zone 'lsm' live/persistent configurations match:
  OK
Bootable disks in zone 'lsm' configuration are:
  c1d1:
    URI: iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25E490003
    Mapped to: /dev/dsk/c0t600144F0DBF8AF1900005FD25E490003d0
Non-bootable disks zone 'lsm' configuration are:
  <none-present>
Verifying input URIs are not already used in zone 'lsm' configuration:
  iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25DFC0002
    OK
  iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25E590004
    OK
Verifying there are no duplicates in the input URIs:
  OK
Verifying the input disks are not part of another zpool:
  Skipping check: '-x force-zpool-attach' is set
Root zpool name in zone 'lsm' is:
  rpool
Checking zpool 'rpool' health:
  ONLINE
Checking zpool 'rpool' vdev configuration:
  OK
Disks in the zone 'lsm' zpool 'rpool' are:
  c1d1 (bootpri=0)
Highest boot disk priority in zpool 'rpool':
  0
Adding new storage devices to zone 'lsm' persistent config:
  c1d2:
    URI: iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25DFC0002
    Mapped to: /dev/dsk/c0t600144F0DBF8AF1900005FD25DFC0002d0
    Boot priority: 0
    Device ID: 2
  c1d3:
    URI: iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25E590004
    Mapped to: /dev/dsk/c0t600144F0DBF8AF1900005FD25E590004d0
    Boot priority: 0
    Device ID: 3
Will apply the configuration changes now:
  Checking: Adding device storage=iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25DFC0002
  Checking: Adding device storage=iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25E590004
  Applying the changes
Attaching new disks.
  c1d2:
    OK
  c1d3:
    OK
Waiting for disks to resilver.
  455M resilvered at 39M/s, 5.58% done, 1m35s to go
  508M resilvered at 38.4M/s, 5.58% done, 1m37s to go
  595M resilvered at 42.2M/s, 5.58% done, 1m28s to go
  692M resilvered at 41.5M/s, 5.58% done, 1m30s to go
  802M resilvered at 41.6M/s, 5.58% done, 1m29s to go
  870M resilvered at 40.1M/s, 10.98% done, 1m27s to go
  930M resilvered at 39.9M/s, 10.98% done, 1m28s to go
  1022M resilvered at 40.4M/s, 10.98% done, 1m27s to go
  1.08G resilvered at 40.6M/s, 10.98% done, 1m26s to go
  1.13G resilvered at 37.1M/s, 10.98% done, 1m34s to go
  1.19G resilvered at 36.8M/s, 10.98% done, 1m35s to go
  1.23G resilvered at 35.8M/s, 15.62% done, 1m33s to go
  1.3G resilvered at 35.7M/s, 15.62% done, 1m33s to go
  1.38G resilvered at 36.1M/s, 15.62% done, 1m32s to go
  1.46G resilvered at 36.1M/s, 15.62% done, 1m32s to go
  1.5G resilvered at 35.6M/s, 15.62% done, 1m33s to go
  1.52G resilvered at 34.8M/s, 19.56% done, 1m31s to go
  1.57G resilvered at 34.3M/s, 19.56% done, 1m32s to go
  1.63G resilvered at 34.2M/s, 19.56% done, 1m33s to go
  1.71G resilvered at 34.3M/s, 19.56% done, 1m32s to go
  1.76G resilvered at 34.2M/s, 19.56% done, 1m32s to go
  1.8G resilvered at 33.4M/s, 23.14% done, 1m31s to go
  1.84G resilvered at 33.3M/s, 23.14% done, 1m31s to go
  1.89G resilvered at 32.8M/s, 23.14% done, 1m32s to go
  1.93G resilvered at 32.5M/s, 23.14% done, 1m33s to go
  2G resilvered at 33M/s, 23.14% done, 1m32s to go
  2.1G resilvered at 33.4M/s, 27.51% done, 1m25s to go
  2.18G resilvered at 33.3M/s, 27.51% done, 1m26s to go
  2.26G resilvered at 33.6M/s, 27.51% done, 1m25s to go
  2.33G resilvered at 33.7M/s, 27.51% done, 1m25s to go
  2.38G resilvered at 33.7M/s, 27.51% done, 1m25s to go
  2.45G resilvered at 33.5M/s, 27.51% done, 1m25s to go
  2.51G resilvered at 33.7M/s, 32.00% done, 1m19s to go
  2.6G resilvered at 33.7M/s, 32.00% done, 1m19s to go
  2.69G resilvered at 34.1M/s, 32.00% done, 1m18s to go
  2.75G resilvered at 34M/s, 32.00% done, 1m19s to go
  2.83G resilvered at 34.7M/s, 32.00% done, 1m17s to go
  2.9G resilvered at 34.4M/s, 37.40% done, 1m12s to go
  2.97G resilvered at 34.8M/s, 37.40% done, 1m11s to go
  3.06G resilvered at 35.9M/s, 37.40% done, 1m09s to go
  3.12G resilvered at 37M/s, 37.40% done, 1m07s to go
  3.2G resilvered at 37.4M/s, 37.40% done, 1m06s to go
  3.31G resilvered at 37.3M/s, 46.55% done, 56s to go
  3.42G resilvered at 36.5M/s, 46.55% done, 57s to go
  3.52G resilvered at 35.8M/s, 46.55% done, 59s to go
  3.6G resilvered at 39.3M/s, 46.55% done, 53s to go
  3.71G resilvered at 42.3M/s, 46.55% done, 49s to go
  3.8G resilvered at 44.7M/s, 46.55% done, 47s to go
  3.88G resilvered at 44.4M/s, 46.55% done, 47s to go
  3.96G resilvered at 44.2M/s, 46.55% done, 47s to go
  4.05G resilvered at 43.4M/s, 63.07% done, 33s to go
  4.15G resilvered at 42.7M/s, 63.07% done, 34s to go
  4.26G resilvered at 42M/s, 63.07% done, 34s to go
  4.37G resilvered at 41.3M/s, 63.07% done, 35s to go
  4.47G resilvered at 40.6M/s, 63.07% done, 35s to go
  4.58G resilvered at 40M/s, 63.07% done, 36s to go
  4.69G resilvered at 38.7M/s, 63.07% done, 37s to go
  4.8G resilvered at 38.2M/s, 63.07% done, 38s to go
  4.88G resilvered at 37.6M/s, 63.07% done, 38s to go
  4.89G resilvered at 37.2M/s, 63.07% done, 39s to go
  4.93G resilvered at 37.1M/s, 63.07% done, 39s to go
  5G resilvered at 37.2M/s, 63.07% done, 39s to go
  5.08G resilvered at 37.1M/s, 63.07% done, 39s to go
  5.12G resilvered at 36.8M/s, 63.07% done, 39s to go
  5.12G resilvered at 36.3M/s, 82.54% done, 19s to go
  5.13G resilvered at 35.9M/s, 82.54% done, 19s to go
  5.14G resilvered at 35.5M/s, 82.54% done, 19s to go
  5.21G resilvered at 35.6M/s, 82.54% done, 19s to go
  5.24G resilvered at 35.3M/s, 82.54% done, 19s to go
  5.27G resilvered at 35M/s, 94.01% done, 6s to go
  5.31G resilvered at 35M/s, 94.01% done, 6s to go
  5.38G resilvered at 35.3M/s, 94.01% done, 6s to go
Verifying all attached disks in root zpool are online:
  c1d2:
    still DEGRADED, 120 more seconds to wait.
    still DEGRADED, 119 more seconds to wait.
    still DEGRADED, 118 more seconds to wait.
    OK
  c1d3:
    OK
Detaching original disks from zone 'lsm' root zpool:
  c1d1:
    OK
Removing original disks from zone 'lsm' configuration.
  c1d1:
    OK
Will apply the configuration with removed original disks now:
  Checking: Removing device storage=iscsi://mystorage/luname.naa.600144F0DBF8AF1900005FD25E490003
  Applying the changes
Live storage migration succeeded.
```



### Quickly testing the feature

You can run the following to try out the feature using local ZFS volumes as that does not need much configuration:

```
host# zonecfg -z mykz create -t SYSsolaris-kz
host# zoneadm -z mykz install
host# zoneadm -z mykz boot
```

Now use `zlogin` below to connect to the zone console, wait for the textual menu-like interface and finish the zone configuration from the console as that is mandatory for storage move to work. Choose "No network" for faster boot unless you configured the KZ to be networked. After reaching the final screen, exit the menu, and wait for the console `login:` promp to show up. You connect to the zone console like this (to disconnect from the console, type `~.`, that is, a tilda followed by a dot):

```
host# zlogin -C mykz
```

You are now ready to live move to a newly created ZFS volume. Remember, the whole storage migration is driven from the host, no need to log in into the guest:

```
host# zfs create -V 16G rpool/VARSHARE/zones/mykz/disk1
host# zoneadm -z mykz move -v -p dev:/dev/zvol/dsk/rpool/VARSHARE/zones/mykz/disk1
```



### Rollback on failure

Anytime there is a failure or you manually kill the operation via Ctrl-C, the KZ will be reverted to its original state, and the `zoneadm` command properly fails. For example:

```
...
...
Attaching new disks.
  c1d1:
    OK
Waiting for disks to resilver.
  8.07M resilvered at 23.2M/s, 0.00% done, 2m37s to go
  31.6M resilvered at 24.5M/s, 0.00% done, 2m28s to go
  46.3M resilvered at 18.7M/s, 0.00% done, 3m15s to go
  55M resilvered at 17.3M/s, 0.00% done, 3m31s to go
  78M resilvered at 16.4M/s, 0.00% done, 3m42s to go
  91.6M resilvered at 16.1M/s, 2.22% done, 3m41s to go
  115M resilvered at 18M/s, 2.22% done, 3m18s to go
  127M resilvered at 16.5M/s, 2.22% done, 3m35s to go
  133M resilvered at 15.9M/s, 2.22% done, 3m44s to go
  159M resilvered at 17.1M/s, 2.22% done, 3m29s to go
^CSignal SIGINT caught.
Please be patient while we properly clean up...
!! Interrupting now may leave your zone in inconsistent state !!
Detaching new disks that might have been already attached.
  c1d1:
    OK
Removing devices already added to the persistent zone config.
  c1d1:
    OK
Reverting live zone configuration to its original state.
  Checking: Removing device storage=dev:/dev/zvol/dsk/rpool/VARSHARE/zones/mykz/disk1
  Applying the changes
Clean-up successful.
==== Completed:   ====
zoneadm: zone 'mykz': 'move' terminated by signal SIGINT.
zoneadm: zone 'mykz': move failed.
```



### Future plans

We plan on adding support for assigning specific disk IDs to URIs when moving the storage. Presently disk IDs are assigned automatically. By disk IDs, we mean those `c1d<N>` disk numbers as seen from within KZ guests. Tentatively, that support should arrive in SRU51 (mid November 2022). The API would be as follows:

```
root# zoneadm -z mykz move -p dev:/dev/zvol/dsk/rpool/VARSHARE/zones/mykz/disk1 -x id=98 \
    -p dev:/dev/zvol/dsk/rpool/VARSHARE/zones/mykz/disk2 -x id=99
```

If the `-x id=<N>` option does not follow a `-p` option, the disk ID for such a URI is assigned automatically as before.

While all our plans are always a subject to change, we also plan KZ live storage operations on individual disks. For example, to replace just one disk in the KZ root zpool mirror, to add a new disk to form or extend an existing mirror, or to remove a disk from an existing mirror.



Copyright (c) 2020, 2023 Oracle and/or its affiliates.

Released under the Universal Permissive License v1.0 as shown at

[https://oss.oracle.com/licenses/upl/](https://oss.oracle.com/licenses/upl/)