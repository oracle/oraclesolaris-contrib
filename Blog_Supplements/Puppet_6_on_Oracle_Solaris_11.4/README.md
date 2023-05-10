## **Puppet 6 on Oracle Solaris 11.4**  

Puppet is an open-source cross-platform orchestration tool that is used to automate tasks such as software provisioning and system configuration management. Puppet uses agent-server architecture in which a primary server controls the configuration that is applied to agent nodes.

As of Oracle Solaris 11.4 Support Repository Update(SRU) 44, both Puppet master and agent components were supported.  Oracle Solaris 11.4 SRU 45 no longer supports Puppet master as the Puppet (WEBrick/Ruby-based) master is deprecated by the Puppet community and hence removed from Oracle Solaris. However, Oracle Solaris 11.4 SRU45 ships Puppet 6.26 agent, so you can continue to use Puppet 6.26 agent with Oracle Solaris while running Puppet Server(master) on a non-Solaris system. For suggestions of alternative ways of running Puppet Server(master), see https://puppet.com/docs/puppet/6/puppet_index.html.

To continue using Puppet 5.5 when upgrading Solaris, the Puppet package should be frozen at 5.5.21. Follow the procedure mentioned in the section [Freezing the Puppet 5.5 Solaris IPS package](#Freeze) below for staying at Puppet 5.5.

Let us now understand the procedure to install and configure Puppet 6 on Oracle Solaris 11.4. For the sake of this blog, let us assume Puppet Server is installed on Oracle Linux. For information on installing Puppet Server on a non-Solaris operating system, refer to https://puppet.com/docs/puppet/6/server/install_from_packages.html#install-puppet-server



### **Installing Puppet 6 on Oracle Solaris 11.4**  

Puppet agent is available as a single package in the Oracle Solaris Image Packaging System repository that configures the system as agent/node.  If Puppet is already installed on the system, Puppet is automatically updated to Puppet 6.26 when you update to Oracle Solaris 11.4SRU45. If Puppet 5.5 master is installed on the system, the Puppet master is automatically deleted.

```
root@agent-node:~#pkg install system/management/puppet
           Packages to install: 17
           Mediators to change:  1
            Services to change:  2
       Create boot environment: No
Create backup boot environment: No

DOWNLOAD                                PKGS         FILES    XFER (MB)   SPEED
Completed                              17/17     4818/4818    11.0/11.0  1.0M/s

PHASE                                          ITEMS
Installing new actions                     5186/5186
Updating package state database                 Done 
Updating package cache                           0/0 
Updating image state                            Done 
Creating fast lookup database                   Done 
Updating package cache                           4/4 
```



### Verify the package is installed  

```
root@agent-node:~# pkg info puppet
             Name: system/management/puppet
          Summary: Puppet agent - The Puppet daemon that runs on the target
                   system (node).
      Description: Puppet is a flexible, customizable framework designed to help
                   system administrators automate the many repetitive tasks they
                   regularly perform. As a declarative, model-based approach to
                   IT automation, it lets you define the desired state - or the
                   "what" - of your infrastructure using the Puppet
                   configuration language. Once these configurations are
                   deployed, Puppet automatically installs the necessary
                   packages and starts the related services, and then regularly
                   enforces the desired state.
         Category: System/Administration and Configuration
            State: Installed
        Publisher: solaris
          Version: 6.26.0
           Branch: 11.4.48.0.0.120.0
   Packaging Date: xxx xxx xx 18:34:15 xxxx
Last Install Time: xxx xxx xx 06:44:28 xxxx
             Size: 5.48 MB
             FMRI: pkg://solaris/system/management/puppet@6.26.0-11.4.48.0.0.120.0:20220421T183415Z
      Project URL: http://puppetlabs.com/
       Source URL: https://github.com/puppetlabs/puppet
```



### **Configuring Puppet 6 agent**  

Let us configure Puppet 6 agent on the system where Puppet package is installed. When you install *system/management/puppet* package on Oracle Solaris 11.4, you will find *svc:application/puppet:agent* service for Puppet agent.

```
root@agent-node:~# svcs -a | grep puppet:agent
disabled       16:04:54 svc:/application/puppet:agent
```

As stated earlier, in this example configuration, Puppet Server is installed and configured on Oracle Linux. Use the below command to make sure the Puppet Server service is running on Oracle Linux.

```
root@puppet-server:~# systemctl status puppetserver
puppetserver.service - puppetserver Service
   Loaded: loaded (/lib/systemd/system/puppetserver.service; enabled; vendor preset: enabled
   Active: active (running) since xxx xxxx-xx-xx 10:34:08 xxxx; 1 weeks 1 days ago
 Main PID: 1099 (java)
    Tasks: 54 (limit: 4915)
   CGroup: /system.slice/puppetserver.service
           1099 /usr/bin/java -Xms512m -Xmx512m -Djruby.logger.class=com.puppetlabs.jruby_
```

We will set the value of config/server property to point to the system running Puppet Server

```
root@agent-node:~# svccfg -s puppet:agent setprop config/server=puppet-server.example.com
root@agent-node:~# svccfg -s puppet:agent refresh
```

Once this is done, we can test our connection by using puppet agent command with the —test option. This also creates a new Secure Sockets Layer (SSL) key and sets up a request for authentication between the agent and the server.

```
root@agent-node:~# puppet agent --test
Exiting; no certificate found and waitforcert is disabled
```

On the Puppet Server system, 'puppetserver ca list —all' command can be used to view the certificates and ‘puppetserver ca sign’ command to sign the certificate.

```
root@puppet-server:~# puppetserver ca list --all 
agent-node.example.com (SHA256) BB:0A:D4:72:6F:F9:22:04:05:2B:FA:12:53:32:E0:4A:A5:09:5F:
01:60:5A:16:46:09:47:ED:FC:77:AD:1B:EF
root@puppet-server:~# puppetserver ca sign —certname agent-node.example.com
Successfully signed certificate request for agent-node.example.com
```

On the Puppet agent system, let us retest our connection and enable the service.

```
root@agent-node:~# puppet agent —test
root@agent-node:~# svcadm enable puppet:agent
root@agent:~# svcs puppet:agent
STATE         STIME    FMRI
online        18:20:32 svc:/application/puppet:agent
```

### **Puppet resource types on Oracle Solaris 11.4:**  

In order to use Puppet resource types such as *nsswitch, pkg_publisher, service* on an Oracle Solaris 11.4 system running Puppet agent, a Puppet module called ‘oracle-solaris_providers’ should be installed on the Puppet Server system.

- Create a directory in the default 

  modulepath

   for Puppet. This is the list of directories where Puppet looks for modules. For example, on *nix: /etc/puppetlabs/code/environments/production/modules:/etc/puppetlabs/code/modules:/opt/puppetlabs/puppet/modules

  ```
  root@puppet-server:~# mkdir -p /etc/puppetlabs/code/environments/production/modules/osp
  ```

- Clone the module from the GitHub repository to the directory specified by *modulepath*.

```
       root@puppet-server:~# cd /etc/puppetlabs/code/environments/production/modules/osp
root@puppet-server:~# git clone https://github.com/oracle/puppet-solaris_providers .
```

- Verify the module installation

```
       root@puppet-server:~# puppet module list 
       /etc/puppetlabs/code/environments/production/modules 
       |_ oracle-solaris_providers (v2.1.1) 
          /etc/puppetlabs/code/modules (no modules installed) 
          /opt/puppetlabs/puppet/modules (no modules installed)
```

- Verify the Puppet resource types

```
     root@puppet-server:~# puppet resource --types
     address_object
     address_properties
     anchor
     boot_environment
     concat_file
     concat_fragment
     dns
     etherstub
     evs
     evs_ipnet
     evs_properties
     evs_vport
     exec
     file
     file_line
     filebucket
     group
     ilb_healthcheck
     ilb_rule
     ilb_server
     ilb_servergroup
     ini_setting
     ini_subsetting
     interface_properties
     ip_interface
     ip_tunnel
     ipmp_interface
     ldap
     link_aggregation
     link_properties
     nis
     notify
     nsswitch
     package
     pkg_facet
     pkg_mediator
     pkg_publisher
     pkg_variant
     process_scheduler
     protocol_properties
     resources
     schedule
     service
     solaris_vlan
     stage
     svccfg
     system_attributes
     tidy
     user
     vni_interface
     vnic
     whit
     zfs_acl
     zone
```

### **Simple Configuration with Puppet Site Manifest**  

After installing and configuring Puppet agent on Oracle Solaris 11.4 and Puppet Server on Oracle Linux, let us perform a simple configuration by writing a Puppet Site Manifest.

The Puppet site manifest(*.pp file*) defines the configuration that you want applied to every agent/node.
For details on specifying manifest for primary Puppet Server, see https://puppet.com/docs/puppet/6/dirs_manifest.html#specifying-manifest-primary-server

As such, the Puppet Server uses the main manifest from the current node’s environment. By default, the main manifest for an environment is <ENVIRONMENTS DIRECTORY>/<ENVIRONMENT>/manifests, for example, */etc/puppetlans/code/environments/production/manifests.*

Let us create a file *site.pp* under the default manifest directory and add contents to it by using *file* and *nsswitch* resource types.

```
root@puppet-server:~# vi /etc/puppetlabs/code/environments/production/manifests/site.pp
file { '/custom-file.txt':
  ensure => 'present',
  content => "Hello World from Puppet Server\n",
}
nsswitch { 'current':
  ensure => 'present',
  alias  => 'files ldap',
}
```

The attribute *ensure* in the *file* resource type makes sure that the file *custom-file.txt* is present in the root directory and includes the *content* *“Hello World from Puppet Server”*.

Similarly, the attribute *ensure* in the *nsswitch* resource type makes sure the *nsswitch* configuration file exists and the attribute *alias* sets the value of *alias* in the nsswitch configuration file to *‘**files ldap**’**.*

After saving this file, you can test the changes by using the *puppet apply* command.
For details on *puppet apply* command, see https://puppet.com/docs/puppet/6/dirs_manifest.html#specifying-manifest-apply

By default, agents contact the Puppet Server in 30-minute intervals (this can be changed in the configuration, if required). We can check that Puppet has enforced this configuration by looking to see whether the `custom-file.txt` file has appeared and checking the Puppet agent log located at `/var/log/puppetlabs/puppet/puppet-agent.log`

We can also apply the manifest manually onto the Puppet agent/node using the command *‘**puppet agent* *-**t**’* on the agent/node where the configuration needs to be applied*.*



```
root@agent-node:~# puppet agent -t
root@agent-node:~# ls -la /custom-file.txt
-rw-------   1 root     root          xx xxx xx 21:50 /custom-file.txt
root@agent-node:~# cat /custom-file.txt
Hello World from Puppet Server
root@agent-node:~# tail /var/log/puppetlabs/puppet/puppet-agent.log
....
20xx-xx-xx 06:30:39 +0000 /File[/var/puppetlabs/puppet/cache/lib/puppet/provider/nsswitch]/ensure (notice): created
20xx-xx-xx 06:31:05 +0000 /Stage[main]/Main/File[/custom-file.txt]/ensure (notice): defined content as '{md5}e4b97f0c18e5bb0bb24d6dbe0db326f4'
20xx-xx-xx 21:50:17 +0000 Puppet (notice): Applied catalog run in 0.21 seconds
```

For information on using other Oracle Solaris specific Puppet resource types, see https://www.oracle.com/technical-resources/articles/it-infrastructure/puppet-on-oracle-solaris-11.html#3

This concludes the setup and configuration of Puppet 6 on Oracle Solaris 11.4.

### **Freezing the Puppet 5.5 Solaris IPS Package**  

Follow these instructions to prevent Puppet to be upgraded when upgrading the Solaris Operating System.

1. Verify which package will be updated using a trial run:

```
    # pkg update -nv
```

2. If the trial run shows that Puppet package will be updated then unlock and freeze the Puppet package to prevent the update:

 a) Unlock the package:

```
    # pkg change-facet facet.version-lock.system/management/puppet=false
```


 b) Freeze Puppet package to prevent it from being updated on subsequent updates:

```
    # pkg freeze system/management/puppet
```

 

3. To Unfreeze the package:

```
    # pkg unfreeze system/management/puppet
```

For detailed information on freezing packages, refer to the 'Locking Packages to a Specified Version' (https://docs.oracle.com/cd/E37838_01/html/E60979/gilfr.html)

### **Impact of Puppet 6 type changes on Oracle Solaris**  

In Puppet 6.0, some of Puppet's built-in types were removed from Puppet source and were moved into individual modules.
Some of these types include:

- `cron`
- `host`
- `mount`
- `scheduled_task`
- `selboolean`
- `selmodule`
- `ssh_authorized_key`
- `sshkey`
- `yumrepo`
- `zfs`
- `zone`
- `zpool`

In order to install these modules, use *puppet module install* command on the system running Puppet Server or on systems running Puppet agents if configuring the systems locally.
For example: puppet module install --target-dir <module-path-dir> <module-name>  
           module-path-dir : Defined by modulepath environment variable

```
root@puppet-server:~# puppet module install --target-dir /etc/puppetlabs/code/environments/production/modules puppetlabs-cron_core
Notice: Preparing to install into /etc/puppetlabs/code/environments/production/modules ... 
Notice: Downloading from https://forgeapi.puppet.com ... 
Notice: Installing -- do not interrupt ... 
/etc/puppetlabs/code/environments/production/modules 
|_ puppetlabs-cron_core (v1.1.0)
```

Verify the module installation by checking the resource type

```
root@puppet-server:~# puppet resource --types
......
cron
.....
```

The same procedure can be used for other modules as well. 



Copyright (c) 2020, 2023 Oracle and/or its affiliates.

Released under the Universal Permissive License v1.0 as shown at

[https://oss.oracle.com/licenses/upl/](https://oss.oracle.com/licenses/upl/)

