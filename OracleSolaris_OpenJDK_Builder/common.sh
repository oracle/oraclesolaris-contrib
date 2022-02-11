WS="`pwd`"
BUILD_DIR="$WS/build_dir"

if [ $VERSION -lt 16 ]; then
   SRC_DIR="jdk${VERSION}u"
else
   SRC_DIR="jdk${VERSION}"
fi

if [ `uname -p` = 'sparc' ] ; then
  JDK_PLATFORM="sparcv9"
else
  JDK_PLATFORM="x86_64"
fi

STUDIO="/opt/solarisstudio12.4/bin"

GCC=/usr/gcc/10/bin/gcc
GXX=/usr/gcc/10/bin/g++

mkdir -p "$BUILD_DIR"
rm -rf "$BUILD_DIR"/$SRC_DIR
test -z $JDK_REPO && JDK_REPO=http://hg.openjdk.java.net/jdk-updates
test -z $JDK_GITHUB_REPO && JDK_GITHUB_REPO=https://github.com/openjdk

function apply_patch_series {
  cat "$WS/patches-$VERSION/series" | while read patch args; do
    echo $patch | grep ^\# > /dev/null && continue
    gpatch --batch --forward --strip=1 $args -i "$WS/patches-$VERSION/$patch"
  done
}
