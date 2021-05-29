# Controlling PF rules with SMF (stencil & profile) and IPS

With the replacement of IP Filter (IPF) with the Oracle Solaris implementation Packet Filter (PF) customers were faced with a few minor and major changes depending on how one used IPF in the past.
In the following I want to show how one of the changes that came with PF helps to easily manage configurations.

One great thing about how PF configuration works, besides using the pfctl command, is that by default PF allows includes in the pf.conf file. This itself is not a fantastic new feature but is much easier to maintain different files each for a certain purpose than one large file only. Especially when we not talking about only a few servers but rather hundreds or even thousands.
Since most servers will most likely not run the same applications or in the same subnets or even networks it was important for me to come up with a way to neither have multiple config files with the same entries and differences in just one line or so.
Whether you are using ansible, puppet, chef, cfengine or which ever configuration tool the way of configuring the firewall should stay same too. Not a big fan of relying on certain tools.
Additionally if you are already using PF with a different BSD derivat you should be able to use the same files. Unless you are using OS specifics in it. But the majority should.
In order to not just talk about how to create rules and anchors and such in PF I will stay with simple PF rules in this case. It really doesn't matter what you use inside of the config files.

So, one of the big differences to other PF implementations is Solaris SMF and two of it's great features - stencils and profiles. As most probably know SMF has been replacing the old/traditional way of configuring the OS. For example if you want to persistently change the nameserver you cannot do that by editing /etc/resolv.conf but by changing the desired value of the service svc:/network/dns/client:default. SMF takes care of changing updating the files. My guess is because of compatibility reasons. Which is nice if you depend on third party software or your own old software and have no time to update it. ;-)
Since not every software is not SMF aware stencils were implemented. Best example to me for this is puppet that comes with the Oracle Solaris repository. There is no need to edit the puppet.conf but instead change the service's property. Thanks to this, by just adding the host configuration part of the the puppet:agent SMF service to your sc_profile.xml when installing a new server (zone, ldom, bare metal, ...) it will configure your puppet agent without you doing anything.
In this case I use a stencil file to add include entries to the pf.conf file.
But in order to add and remove changes to the service I will us SMF profiles, which are nothing more than SMF xml snippets with the modification I want for a certain service. In this case it adds the awareness to the service of a new config file to be used with the SMF stencil.

In addition to the use of SMF stencils I will use IPS packages in order to easily add or remove files and there for PF configurations.

So this is what we will need:
1. PF rule files
2. SMF profile
3. SMF stencil
4. IPS package

## PF rules
The easiest part is to create a file for each rule or each set of rules that you want to be able to control seperately from other rules.
Let's just pick a few for the purpose of this post.

- ssh
- rsyslog

- ips (repository)
- rad
- puppet
- solaris webui

The rules can either be added into one file or multiple files as mentioned before. They also could be added to the stencil file later on which will create the pf.conf file. Just to show you how you can have certain rules in pace by default I will have ssh and rsyslog be added later on and just use the others in separate files.

pf.ips
```bash
## accept connections for Solaris IPS repository
pass in proto tcp from any to any port = 8113
pass in proto tcp from any to any port = 8114
```

pf.rad:
```bash
## accept connections for oracle solaris rad:remote
pass in proto tcp from any to any port = 12302
pass in proto tcp from any to any port = 8102
```

pf.puppet:
```bash
## accept connections for oracle puppet
pass in proto tcp from any to any port = 8140
```

pf.webui
```bash
## accept connections for oracle solaris webui dashboard
pass in proto tcp from any to any port = 6787
```

In order to later on create ips packages with these files I would recommend to just directly create all the files in the preferred proto directory.

It pretty much doesn't matter where you will store the files later on as long as you will pass on the right path to the according SMF profile in the next step.

You can also directly create the files in /etc/firewall. IPS is just so much easier to work with and automate.

## SMF profiles
As mentioned earlier SMF profiles contain only the part of a service that needs to be changed or added. The default path for custom profiles is /etc/svc/profile/site.
So far we have a file (pf.webui) that includes the trivial rule to pass connections from anywhere to port 6787. In my case, I have all pf files in the `/etc/firewall` directory. In order for our stencil to later on be able to find these files we have to add their path to the firewall service. This is done by creating a property group for all includes (pf.webui, pf.rad, ...) and a property entry for the path itself. The SMF service xml file that we create will be automatically picked up and configured by `svc:/system/manifest-import:default` from the site directory.

Let's just use the webui as a quick example.
firewall-webui-profile.xml
```xml
<service_bundle type='profile' name='network/firewall'>
        <service name='network/firewall' type='service' version='1'>
                <property_group name='include' type='framework'>
                        <propval name='webui' type='astring' value='/etc/firewall/pf.webui'/>
                </property_group>
        </service>
</service_bundle>
```

When this is put into place (/etc/svc/profile/site) and manifest-import was restarted, the service property of the firewall service should look like this.
```bash
K muehle@wacken % svcprop -p include/webui firewall
include/webui astring /etc/firewall/pf.webui
```

firewall-ips-profile.xml
```xml
<service_bundle type='profile' name='network/firewall'>
        <service name='network/firewall' type='service' version='1'>
                <property_group name='include' type='framework'>
                        <propval name='ips' type='astring' value='/etc/firewall/pf.ips'/>
                </property_group>
        </service>
</service_bundle>
```

firewall-rad-profile.xml
```xml
<service_bundle type='profile' name='network/firewall'>
        <service name='network/firewall' type='service' version='1'>
                <property_group name='include' type='framework'>
                        <propval name='rad' type='astring' value='/etc/firewall/pf.rad'/>
                </property_group>
        </service>
</service_bundle>
```

firewall-puppet-profile.xml
```xml
<service_bundle type='profile' name='network/firewall'>
        <service name='network/firewall' type='service' version='1'>
                <property_group name='include' type='framework'>
                        <propval name='puppet' type='astring' value='/etc/firewall/pf.puppet'/>
                </property_group>
        </service>
</service_bundle>
```

As a result we will get the following:
```bash
K muehle@wacken % svcprop -p include firewall
include/ips astring /etc/firewall/pf.ips
include/puppet astring /etc/firewall/pf.puppet
include/rad astring /etc/firewall/pf.rad
include/webui astring /etc/firewall/pf.webui
```

So far we have pf files which include the pf rules that will be created in /etc/firewall and the SMF profile files, which contain information about the path of the pf files for the firewall service.

Since we will use SMF stencils the service needs to be aware of it too. And the best way to modify a service is by using SMF profiles. So let's create one for this case too.

firewall-stencil-profile.xml
```xml
<service_bundle type='profile' name='network/firewall'>
        <service name='network/firewall' type='service' version='1'>
                <property_group name="firewall_stencil" type="configfile">
                        <propval name="path" type="astring" value="/etc/firewall/pf.conf"/>
                        <propval name="stencil" type="astring" value="firewall.stencil"/>
                        <propval name="mode" type="astring" value="0644"/>
                </property_group>
        </service>
</service_bundle>
```
Three properties are needed:
- path - configuration file that needs to be created and written to by SMF
- stencil - name of the stencil file that is used for this service (default location: /lib/svc/stencils)
- mode - file permissions for pf.conf

The thing missing now is how exactly PF itself will know about the pf files and therefore configuration changes. And this is where we need to create the SMF stencil file.


## SMF stencil (firewall.stencil)
As we know the default PF config file (pf.conf) can be found under /etc/firewall. This is the one config file that PF itself uses by default. The stencil that we will create is going to replace this file. We can either use the default pf.conf as basis to start our stencil or just create our own. Both work the same since the only thing that matters are the rules or other configurations used inside.
Because of the whole Copyright stuff in the default file I start from scratch and create a small stencil that enables us to add as many configs as we want.
Because of the whole Copyright stuff in the default file I start from scratch here and create a small stencil that enables us to add as many configs as we want.

This is what my stencil file looks like for this purpose. 
Please be aware, these rules are just radomly picked for this example. Depending on the requirements your rules need to be adjusted and will most probably be quiet different.

```bash
# /etc/firewall/pf.conf

## ensure IP reassembly working with broken stacks
set reassemble yes no-df

## don't use loopback
set skip on lo0

## block everything unless told otherwise
## and send TCP-RST/ICMP unreachable
## for every packet which gets blocked
block return log

## accept incoming icmp pkts e.g. ping
pass in proto icmp from any to any

## accept incoming SSH connections
pass in proto tcp to any port 22 flags any keep state (sloppy)

## accept connections for rsyslog
pass in proto tcp from any to any port = 6514

## includes
; walk each instance and extract all properties from the config PG
$%/(svc:/$%s:(.*)/:properties)/{$%/$%1/include/(.*)/{include "$%{$%1/include/$%3}"
}}

## allow all connections initiated from this system,
## including DHCP requests
pass out
```

As you can see it is just basic stuff. I like to have certain rules in place on every system, like the earlier mentioned ssh and rsyslog, that I wanted to use as example how to directly add configurations or rules to the pf.conf. Downside to this is, you would have to replace the whole stencil file if you want to change or remove the rule.
The stencil file could as well be blank and only have the "includes" part in it.

The `ìncludes` section tells SMF to look for the `include` property group in every instance of the service (in this case svc:/network/firewall:default) and add the value to the by firewall-stencil-profile.xml configured file/path. In this case /etc/firewall/pf.conf we used the default so we would not have to reconfigure PF itself.

The pf.conf should look like this once all the above is in place:
```bash
# /etc/firewall/pf.conf

## ensure IP reassembly working with broken stacks
set reassemble yes no-df

## don't use loopback
set skip on lo0

## block everything unless told otherwise
## and send TCP-RST/ICMP unreachable
## for every packet which gets blocked
block return log

## accept incoming icmp pkts e.g. ping
pass in proto icmp from any to any

## accept incoming SSH connections
pass in proto tcp to any port 22 flags any keep state (sloppy)

## accept connections for rsyslog
pass in proto tcp from any to any port = 6514


## includes
include /etc/firewall/pf.ips
include /etc/firewall/pf.puppet
include /etc/firewall/pf.rad
include /etc/firewall/pf.webui

## allow all connections initiated from this system,
## including DHCP requests
pass out
```

And since we do not want more administrative overhead than before we just create IPS packages for each rule(set)

## IPS

Why IPS? Because all a configuration tool or admin has to do is make sure a package is installed or not. That is the whole magic of adding and removing rules once all the needed files are packaged up.

I have a directory for each rule(set). Here is a small example of it:
```bash
K muehle@wacken % ls -1
...
PF_FIREWALL_AI
PF_FIREWALL_APACHE
PF_FIREWALL_DB2
PF_FIREWALL_ELASTIC
PF_FIREWALL_IPS
PF_FIREWALL_JBOSS
PF_FIREWALL_LDAP
PF_FIREWALL_MYSQL
PF_FIREWALL_NAGIOS
PF_FIREWALL_NETBACKUP
PF_FIREWALL_NFS
PF_FIREWALL_ODB
PF_FIREWALL_OEM
PF_FIREWALL_PUPPET
PF_FIREWALL_RAD
PF_FIREWALL_RSYSLOG
PF_FIREWALL_SAP
PF_FIREWALL_SCOM
PF_FIREWALL_SMB
PF_FIREWALL_SPLUNK
PF_FIREWALL_SSH
PF_FIREWALL_STENCIL
PF_FIREWALL_TOMCAT
PF_FIREWALL_TQ
PF_FIREWALL_TSM
PF_FIREWALL_VDCF
PF_FIREWALL_WEBUI
PF_FIREWALL_WLS
...
```

Webui proto directory structure would be:
```bash
PF_FIREWALL_WEBUI
PF_FIREWALL_WEBUI/PROTO
PF_FIREWALL_WEBUI/PROTO/etc
PF_FIREWALL_WEBUI/PROTO/etc/firewall
PF_FIREWALL_WEBUI/PROTO/etc/firewall/pf.webui
PF_FIREWALL_WEBUI/PROTO/etc/svc
PF_FIREWALL_WEBUI/PROTO/etc/svc/profile
PF_FIREWALL_WEBUI/PROTO/etc/svc/profile/site
PF_FIREWALL_WEBUI/PROTO/etc/svc/profile/site/firewall-webui-profile.xml
```
While the stencil proto structure should sort of look like this:
```bash
PF_FIREWALL_STENCIL
PF_FIREWALL_STENCIL/PROTO
PF_FIREWALL_STENCIL/PROTO/etc
PF_FIREWALL_STENCIL/PROTO/etc/svc/
PF_FIREWALL_STENCIL/PROTO/etc/svc/profile
PF_FIREWALL_STENCIL/PROTO/etc/svc/profile/site
PF_FIREWALL_STENCIL/PROTO/etc/svc/profile/site/firewall-stencil-profile.xml
PF_FIREWALL_STENCIL/PROTO/lib
PF_FIREWALL_STENCIL/PROTO/lib/svc
PF_FIREWALL_STENCIL/PROTO/lib/svc/stencils
PF_FIREWALL_STENCIL/PROTO/lib/svc/stencils/firewall.stencil
```

At this point I will not go all over how to create an IPS package. There are lots of posts on that topic already.
A possible MOG file for creating the IPS package could look like this:

```bash
set name=pkg.fmri value=pkg://odev/security/pf-firewall-webui@1.0
set name=pkg.summary value="PF FIREWALL conf /etc/firewall/pf.webui (build with st_085)"
set name=pkg.description value="This package contains the webui configuration for the pf firewall and the corresponding service."
set name=variant.arch value=sparc value=i386
<transform dir path=etc$ -> drop>
<transform dir path=etc/svc$ -> drop>
<transform dir path=etc/svc/profile$ -> drop>
<transform dir path=etc/svc/profile/site$ -> drop>
<transform file path=etc/svc/profile/site/firewall-webui-profile.xml$ -> set owner root>
<transform file path=etc/svc/profile/site/firewall-webui-profile.xml$ -> set group sys>
<transform file path=etc/svc/profile/site/firewall-webui-profile.xml$ -> set mode 0444>
<transform file path=etc/svc/profile/site/firewall-webui-profile.xml$ -> default restart_fmri svc:/system/manifest-import:default>
<transform dir path=etc/firewall$ -> drop>
<transform file path=etc/firewall/pf.webui$ -> set owner root>
<transform file path=etc/firewall/pf.webui$ -> set group sys>
<transform file path=etc/firewall/pf.webui$ -> set mode 0644>
<transform file path=etc/firewall/pf.webui$ -> default refresh_fmri svc:/network/firewall:default>
```

Or instead directly pf-firewall-webui.p5m.4.res:
```bash
set name=pkg.fmri value=pkg://odev/security/pf-firewall-webui@1.0
set name=pkg.summary value="PF FIREWALL conf /etc/firewall/pf.webui (build with st_085)"
set name=pkg.description value="This package contains the webui configuration for the pf firewall and the corresponding service."
set name=variant.arch value=i386 value=sparc
file etc/firewall/pf.webui path=etc/firewall/pf.webui owner=root group=sys mode=0644 refresh_fmri=svc:/network/firewall:default
file etc/svc/profile/site/firewall-webui-profile.xml path=etc/svc/profile/site/firewall-webui-profile.xml owner=root group=sys mode=0444 restart_fmri=svc:/system/manifest-import:default
```

All that is left to do now is add the needed packages to your CMS of choice or just go ahead and install it via pkg install.
The stencil package always needs to be installed in order for this to work. Once you then install a package with pf configurations it will automatically be added. Check it out with `pfctl -s rule`.
```bash
block return log (to pflog0) all
pass in proto icmp all
pass in proto tcp from any to any port = 22 flags any keep state (sloppy)
pass in proto tcp from any to any port = 6514 flags S/SA
pass in proto tcp from any to any port = 8113 flags S/SA
pass in proto tcp from any to any port = 8114 flags S/SA
pass in proto tcp from any to any port = 8140 flags S/SA
pass in proto tcp from any to any port = 12302 flags S/SA
pass in proto tcp from any to any port = 8102 flags S/SA
pass in proto tcp from any to any port = 6787 flags S/SA
```

Uninstall the package in order to remove the rule.

## Conclusion
Long story short, create the following:
1. one IPS package including:
    - `SMF stencil` file
    - `SMF profile` file
2. multiple (as many as it suits your needs) IPS packages including:
    - `pf files` (that include the rules)
    - `SMF profile` file

The purpose of the post was not to show how exactly each of the features that we used work in detail but rather how easy it is to combine these given possibilities to create something really helpful for automation and getting rid of some administrative overhead.

Hopefully this might be a bit of a help to someone.
