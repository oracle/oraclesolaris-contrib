set -xe

VERSION=10

. common.sh

# S11.4.21 have updated CUPS version which causes problem to old Studio compiler
function fix_cups_versioning {
  test `uname -v | cut -d . -f 3` -lt 21 && return
  gsed 's;_CUPS_NONNULL(...);_CUPS_NONNULL();' /usr/include/cups/versioning.h > my-cups-versioning.h
  FILE=CUPSfuncs.c
  for f in jdk/src/java.desktop/unix/native/common/awt/$FILE src/java.desktop/unix/native/common/awt/$FILE; do
    [ ! -f "$f" ] || gsed -i "/#include <dlfcn.h>/a#include \"`pwd`/my-cups-versioning.h\"" "$f"
  done
}

BOOT_JDK="$BUILD_DIR/jdk9u/build/solaris-$JDK_PLATFORM-normal-server-release/jdk"
PATH="$STUDIO:/usr/bin"

CONFIGURE_OPTIONS+=" --with-boot-jdk=$BOOT_JDK"

hg clone ${JDK_REPO}/$SRC_DIR "$BUILD_DIR"/$SRC_DIR
cd "$BUILD_DIR"/$SRC_DIR

fix_cups_versioning
apply_patch_series

PATH="$PATH" bash ./configure ${CONFIGURE_OPTIONS} 
gmake bundles 
