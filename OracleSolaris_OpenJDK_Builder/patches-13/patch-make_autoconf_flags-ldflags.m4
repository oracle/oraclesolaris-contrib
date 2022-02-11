--- make/autoconf/flags-ldflags.m4~	Wed Jul 15 16:48:24 2020
+++ make/autoconf/flags-ldflags.m4	Wed Jul 15 16:53:10 2020
@@ -71,8 +71,12 @@
 
     # Add -z defs, to forbid undefined symbols in object files.
     # add relro (mark relocations read only) for all libs
-    BASIC_LDFLAGS="$BASIC_LDFLAGS -Wl,-z,defs -Wl,-z,relro"
-    BASIC_LDFLAGS_JVM_ONLY="-Wl,-O1"
+    if test "x$OPENJDK_TARGET_OS" = xsolaris; then
+      BASIC_LDFLAGS="$BASIC_LDFLAGS -Wl,-z,defs"
+    else
+      BASIC_LDFLAGS="$BASIC_LDFLAGS -Wl,-z,defs -Wl,-z,relro"
+      BASIC_LDFLAGS_JVM_ONLY="-Wl,-O1"
+    fi
 
   elif test "x$TOOLCHAIN_TYPE" = xclang; then
     BASIC_LDFLAGS_JVM_ONLY="-mno-omit-leaf-frame-pointer -mstack-alignment=16 \
