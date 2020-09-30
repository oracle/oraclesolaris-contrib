#!/bin/sh
PROXY="www-proxy.us.oracle.com:80"
BUILDZFS=scratch-$$

zfs create -o mountpoint=/$BUILDZFS rpool/$BUILDZFS

cd /$BUILDZFS

#pkg install git libtool autoconf automake pkg-config gcc gnu-make
# manifest requires to have 
#	git
#	libtool
# 	autoconf
#	automake
#	pkg-config
#	gcc
#	gnu-make
# to be installed already

echo Executing libzmq build in `pwd`
export https_proxy=$PROXY
export http_proxy=$PROXY
git clone https://github.com/zeromq/libzmq

cd libzmq
./autogen.sh
MAKE=gmake ./configure
gmake
