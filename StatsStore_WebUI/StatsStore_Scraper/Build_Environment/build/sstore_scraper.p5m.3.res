set name=pkg.fmri value=stats/statsstore/sstore_scraper@0.3
set name=pkg.summary \
    value="The StatsStore Scraper pulls data from the Oracle Solaris StatsStore, converts the data, and exports this into something like the Splunk HEC"
set name=pkg.description value="StatsStore Scraper and Exporter"
set name=info.classification \
    value="org.opensolaris.category.2008:System/Administration and Configuration"
set name=org.opensolaris.smf.fmri value=svc:/site/sstore-scraper \
    value=svc:/site/sstore-scraper:default
file lib/svc/manifest/site/sstore_scraper.xml \
    path=lib/svc/manifest/site/sstore_scraper.xml owner=root group=bin \
    mode=0644 restart_fmri=svc:/system/manifest-import:default
dir  path=opt/sstore_scraper owner=root group=sys mode=0755
dir  path=opt/sstore_scraper/bin owner=root group=sys mode=0755
file opt/sstore_scraper/bin/sstore_scraper.py \
    path=opt/sstore_scraper/bin/sstore_scraper.py owner=root group=sys \
    mode=0755
file opt/sstore_scraper/bin/sstore_uri_list.py \
    path=opt/sstore_scraper/bin/sstore_uri_list.py owner=root group=sys \
    mode=0644
dir  path=opt/sstore_scraper/etc owner=root group=sys mode=0755
file opt/sstore_scraper/etc/server_info.yaml \
    path=opt/sstore_scraper/etc/server_info.yaml owner=root group=sys mode=0644 \
    preserve=true
file opt/sstore_scraper/etc/sstore_list.yaml \
    path=opt/sstore_scraper/etc/sstore_list.yaml owner=root group=sys mode=0644 \
    preserve=true
depend fmri=pkg:/runtime/python-37 fmri=pkg:/runtime/python-39 type=require-any
depend fmri=pkg:/system/core-os type=require
depend fmri=pkg:/library/python/pyyaml type=require
