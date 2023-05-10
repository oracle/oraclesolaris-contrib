## Changing memory size of running Solaris Kernel Zones

In Oracle Solaris SRU45 released in May 2022, the Zones team delivered another major feature. This one is to allow for reconfiguring memory size of running [Kernel Zones](https://docs.oracle.com/en/operating-systems/solaris/oracle-solaris/11.4/kernel-zones/oracle-solaris-kernel-zones.html) (KZs) on SPARC. Up until this SRU, we could only change the memory size of a Kernel Zone upon booting and/or rebooting it. If you had a long running KZ and you were getting out of memory, the only option possible was to increase the memory size in the zone's configuration `capped-memory` resource, then rebooting the zone. We are very glad this is no longer the case on SPARC.

Note that this feature is about `solaris-kz(7)` branded zones only, also known as Kernel Zones. If you run native or S10 zones (i.e. `solaris(7)` or `solaris10(7)` branded zones), it works the other way around. There, one needs to explicitly limit zone memory caps in their configuration if you do not want them to consume as much as it is asked for. We will not discuss native nor `solaris10` branded zones any further in this article.

For the feature to work, the guest Solaris system version is not relevant as long as it is at least 11.3 SRU8, released in 2016. That also means any Solaris 11.4 version is supported as the guest system. What is relevant is the host system version which must be 11.4 SRU45 or greater.



### What about x86?

It is being worked on! The SPARC part was easier as its memory architecture is simpler than x86 and we wanted this feature to be useful for our SPARC customers even before x86 work is done. We hope to deliver the x86 part of the feature during this year (2022).

**Update: the x86 part was integrated in our code base and is expected to be released with Oracle Solaris SRU51 in Nov 2022.**



### Enabling KZ memory live zone reconfiguration

To allow for changing KZ memory size on the fly, a new memory layout for a KZ guest must be used. For that reason, the KZ must be booted (rebooted) with this new memory layout. To notify the operating system the KZ is to use the new memory layout, one needs to add the `memlzr` modifier to the `host-compatible` zone configuration property. If you do not use the new `memlzr` modifier, the KZ will boot up fine, of course, but the memory live zone reconfiguration (LZR) feature will not be available for this zone. After configuring the `host-compatible` property, you need to reboot the KZ. Instead of the `memlzr` modifier, you can also use either the `level2` or `native` levels as a value for `host-compatible`. Please see the `solaris-kz(7)` manual page for the details, in section *Memory Live Zone Reconfiguration*. For example:

```
# zonecfg -z somekz
zonecfg:somekz> set host-compatible=level2
zonecfg:somekz> commit
zonecfg:somekz> exit
# zoneadm -z somekz reboot
```

Unfortunately, you cannot live migrate your running KZ to another target host, update your source host to SRU45, migrate the KZ back and increase its memory size on the fly. The KZ just must boot up with the new memory layout to support this feature. Note that from this SRU45 on, if you create a new KZ, the `memlzr` modifier will be put into the zone configuration by default as that is what is now in the default `SYSsolaris-kz` template. The templates reside in `/etc/zones` with all other zone configurations.



### Configuring KZ memory live zone reconfiguration

The `host-compatible` settings mentioned above is the only requirement. However, you may also want to control the KZ guest page size. The page size here means the size of memory pages the guest address space consists of as seen by the hypervisor, and it has no relation to the page size the guest system itself can see from within.

You can either use what we have had since the KZ introduction, that is to set `pagesize-policy` property of the `capped-memory` resource to one of `largest-only`, `largest-available`, or `smallest-only`.

Since SRU45 however, you can also set `pagesize-policy` to `fixed` and then set the new property `pagesize` to one of allowable size. That is to better control the granularity of memory resizing. You can use anything greater or equal to 256M from the list of page sizes `pagesize -a` prints out on the host:

```
sparc-host# pagesize -a
8192
65536
4194304
268435456
2147483648
17179869184
```

In this case, we can use 256M, 2G, and 16G as possible values to `pagesize`.

As the guest address space consists of pages of specific size, you can only decrement or increment the KZ memory by the page size. If you create a KZ with 16G of memory and either set `pagesize-policy` to `largest-only` or use `pagesize=16G`, you will not be able to decrease the KZ memory requirements, and only increase it to 32G, 48G, 64G, and so on. For that reason, to test the feature, we recommend to use the `fixed` policy and set `pagesize=256M`.



### Using KZ memory live zone reconfiguration feature

As with any other live zone reconfiguration, you either modify the permanent zone configuration, then apply it to the running zone, or you can directly modify the running configuration. Use whatever suites you. Note that if you use the latter and then you realize you want to keep the configuration change, you must manually modify the permanent zone configuration. In our examples, we directly modify the KZ running configuration via `zonecfg -r`.

Let's start with a running KZ not supporting the feature yet. Enable the feature and set the guest page size to 256M:

```
root:sparc-host::~# zonecfg -z mykz
zonecfg:mykz> set host-compatible=memlzr
zonecfg:mykz> select capped-memory
zonecfg:mykz:capped-memory> set pagesize-policy=fixed
zonecfg:mykz:capped-memory> set pagesize=256M
zonecfg:mykz:capped-memory> end
zonecfg:mykz> commit
zonecfg:mykz> exit
```

Now reboot the zone: `zoneadm -z mykz reboot`

After the KZ boots up, verify it has 8G of memory. We can see we have 1M of 8K sized pages (as mentioned before, this page size has nothing to do with the guest address space page size we configured above), meaning we have 8G of memory as expected.

```
root@mykz:~# pagesize
8192
root@mykz:~# kstat unix:0:system_pages:physmem
module: unix                            instance: 0
name:   system_pages                    class:    pages
        physmem                         1048576
```



### Increasing the KZ memory size on the fly

Now let's change directly the running configuration, to increase the KZ memory to 12G. Remember, this is done from within the host:

```
root:sparc-host::~# zonecfg -z mykz -r
zonecfg:mykz> select capped-memory
zonecfg:mykz:capped-memory> set physical=12G
zonecfg:mykz:capped-memory> end
zonecfg:mykz> commit
Checking: Modifying capped-memory physical=12G
Applying the changes
zonecfg:mykz>
```

Now check the KZ itself:

```
root@mykz:~# kstat unix:0:system_pages:physmem
module: unix                            instance: 0
name:   system_pages                    class:    pages
        physmem                         1572864

root@mykz:~# bc
1572864 * 8 / 1024 / 1024
12
```

There is more ways to find out what is the memory size of a Solaris system instance, you could also do:

```
root@mykz:~# prtconf -v | grep ^Memory
Memory size: 12288 Megabytes
```



### Decreasing the KZ memory size on the fly

We can also decrease the memory the KZ is using, **iff** there is free memory to remove. In our case, we tried to go from 12G to 4G and as we can see, we could not go all the way down but by design the operation does not fail in such a case. The operation will remove as much as possible up to the required limit, and let you know the outcome in a warning message:

```
root:sparc-host::~# zonecfg -z mykz -r
zonecfg:mykz> select capped-memory
zonecfg:mykz:capped-memory> set physical=4G
zonecfg:mykz:capped-memory> end
zonecfg:mykz> commit
Checking: Modifying capped-memory physical=4G
Applying the changes
warning: operation succeeded partially for capped memory (requested: 4G, final: 4.75G)
zonecfg:mykz>

root:sparc-host::~# zlogin mykz
[Connected to zone 'mykz' pts/7]
Last login: Mon Jun 20 14:15:46 2022 on kz/term
Oracle Solaris 11.4.48.123.0                      Assembled June 2022
root@mykz:~# prtconf -v | grep ^Memory
Memory size: 4864 Megabytes
```

We can see above that going down to 4G was not possible but we removed almost all required memory and stopped at about 4.8G.

It does not mean the KZ will not have any free memory right now, only that we could not remove as many pages as possible, nor to move memory around to free more 256M sized pages. We can see the KZ still has enough free memory to operate for now, see the `Free` line below:

```
root@mykz:~# mdb -k
Loading modules: [ unix genunix specfs dtrace zfs kcf rpcmod scsi_vhci zvblk
zvmisc ldc mac ds sockfs ip hook neti dev arp random mdesc ksplice idm sas cpc
fctl fcp fcip ptm smbsrv nfs ufs logindmux nsmb ]
> ::memstat -v
Usage Type/Subtype                      Pages    Bytes  %Tot  %Tot/%Subt
---------------------------- ---------------- -------- ----- -----------
Kernel                                 182927     1.4g 29.3%
  Regular Kernel                       144111     1.1g       23.1%/78.7%
  ZFS ARC Fragmentation                 38816     303m        6.2%/21.2%
ZFS                                     47438     371m  7.6%
  ZFS Metadata                           5239    40.9m        0.8%/11.0%
  ZFS Data                               8654    67.6m        1.3%/18.2%
  ZFS Data                               8854    69.2m        1.4%/18.6%
  ZFS Data                              10596    82.8m        1.7%/22.3%
  ZFS Data                               7832    61.2m        1.2%/16.5%
  ZFS Kernel Data                        6263    48.9m        1.0%/13.2%
User/Anon                               44810     350m  7.1%
Exec and libs                            1001    7.82m  0.1%
Page Cache                               5804    45.3m  0.9%
Free (cachelist)                         4890    38.2m  0.7%
Free                                   335402    2.56g 53.8%
  Regular Free                         330090    2.52g       53.0%/98.4%
  Physical pool reserved mem             5312    41.5m        0.8%/ 1.5%
Total                                  622592    4.75g  100%
```



### Live migration compatibility

Give that the KZ guests supporting the feature have the new memory layout, you can only live migrate those to hosts that also support the feature, that is those running SRU45+. If we try to live migrate our KZ to a host with an older Solaris system version, we fail when trying to import the KZ configuration.

```
root:sparc-host::~# zoneadm -z mykz migrate ssh://mem@hum.us.oracle.com
zoneadm: zone 'mykz': Importing zone configuration on destination.
zoneadm: zone 'mykz': configuration failed:
-----BEGIN CONFIGURATION-----
create -b
set brand=solaris-kz
set host-compatible=memlzr
...
add capped-memory
set physical=12G
set pagesize-policy=fixed
set pagesize=256M
end
...
-----END CONFIGURATION-----
Error received from the target machine:
On line 3:
memlzr: Invalid argument
```

As expected, we do fail to migrate even if we do find an existing KZ configuration on the target host (which does not support the feature).



### Conclusion

Being able to change the memory size of a running Kernel Zone was one of the most desired features we were being asked to deliver. The Zones team is very glad this has been implemented now, and we presently work on delivering the feature for x86 as well.



Copyright (c) 2020, 2023 Oracle and/or its affiliates.

Released under the Universal Permissive License v1.0 as shown at

[https://oss.oracle.com/licenses/upl/](https://oss.oracle.com/licenses/upl/)