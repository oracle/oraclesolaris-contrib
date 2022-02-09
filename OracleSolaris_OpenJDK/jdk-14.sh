set -xe

VERSION=14

. common.sh

BOOT_JDK="$BUILD_DIR/jdk13u/build/solaris-$JDK_PLATFORM-server-release/jdk"
PATH="/usr/bin:/usr/gnu/bin"

CONFIGURE_OPTIONS+=" --enable-unlimited-crypto"
CONFIGURE_OPTIONS+=" --enable-deprecated-ports=yes"
CONFIGURE_OPTIONS+=" --with-boot-jdk=$BOOT_JDK"
CONFIGURE_OPTIONS+=" --with-native-debug-symbols=none"
CONFIGURE_OPTIONS+=" --with-toolchain-type=gcc"
CONFIGURE_OPTIONS+=" --disable-hotspot-gtest"
CONFIGURE_OPTIONS+=" --disable-dtrace"
CONFIGURE_OPTIONS+=" --disable-warnings-as-errors"
CONFIGURE_OPTIONS+=" AS=/usr/gnu/bin/as"
CONFIGURE_OPTIONS+=" CC=$GCC"
CONFIGURE_OPTIONS+=" CXX=$GXX"

hg clone ${JDK_REPO}/$SRC_DIR "$BUILD_DIR"/$SRC_DIR
cd "$BUILD_DIR"/$SRC_DIR

apply_patch_series

PATH="$PATH" bash ./configure ${CONFIGURE_OPTIONS} 
gmake bundles 
