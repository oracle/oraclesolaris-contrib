set -xe

VERSION=11

. common.sh

BOOT_JDK="$BUILD_DIR/jdk10u/build/solaris-$JDK_PLATFORM-normal-server-release/jdk"
PATH="$STUDIO:/usr/bin"

CONFIGURE_OPTIONS+=" --with-boot-jdk=$BOOT_JDK"

hg clone ${JDK_REPO}/$SRC_DIR "$BUILD_DIR"/$SRC_DIR
cd "$BUILD_DIR"/$SRC_DIR

apply_patch_series

PATH="$PATH" bash ./configure ${CONFIGURE_OPTIONS} 
gmake bundles 
