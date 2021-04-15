set name=pkg.fmri value=pkg://vpbank/vpbank/security/pf-firewall-webui@1.0
set name=pkg.summary value="PF FIREWALL conf /etc/firewall/pf.webui (build with 11.4 SRU 7)"
set name=pkg.description value="This package contains the webui configuration for the pf firewall and the corresponding service."
set name=variant.arch value=i386 value=sparc
file etc/firewall/pf.webui path=etc/firewall/pf.webui owner=root group=sys mode=0644 refresh_fmri=svc:/network/firewall:default
file etc/svc/profile/site/firewall-webui-profile.xml path=etc/svc/profile/site/firewall-webui-profile.xml owner=root group=sys mode=0444 restart_fmri=svc:/system/manifest-import:default
