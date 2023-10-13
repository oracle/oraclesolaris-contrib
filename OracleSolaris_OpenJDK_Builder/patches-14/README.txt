This is derived from the pkgsrc-joyent set for openjdk11, building on
my openjdk13 set.

All patches -p0

This set updated for 14.0.1+7

JDK14:
openjdk14 fixes (besides fixing line number noise)

NOTE:

make/hotspot/lib/CompileDtraceLibraries.gmk
is Studio-specific, but we disable dtrace anyway so never hit it

cc1plus: warning: unrecognized command line option '-Wno-cast-function-type'
That's to do with freetype, I think.

remove:

patch-make_launcher_Launcher-jdk.pack.gmk
tribblix-Launcher-jdk.patch
  patched file no longer exists

patch-make_autoconf_flags-ldflags.m4
  broken as of 14.0.1

modified:

patch-make_autoconf_flags-ldflags.m4
  remove hunk1

tribblix-flags-cflags.patch
  surrounds changed

add:

tribblix-flags-ldflags.patch
tribblix-flags-ldflags2.patch
tribblix-flags-ldflags3.patch

tribblix-wait.patch
  wait() is a standard function, it's asking for trouble to define
  your own with the same name

Build:

env PATH=/usr/bin:/usr/sbin:/usr/sfw/bin:/usr/gnu/bin bash ./configure \
--enable-unlimited-crypto --with-boot-jdk=/usr/jdk/instances/jdk13 \
--with-native-debug-symbols=none \
--with-toolchain-type=gcc \
--disable-hotspot-gtest --disable-dtrace \
--disable-warnings-as-errors \
--enable-deprecated-ports=yes

env PATH=/usr/bin:/usr/sbin:/usr/sfw/bin:/usr/gnu/bin gmake all
