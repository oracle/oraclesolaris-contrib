$NetBSD$

Shell portability, and remove annoying warning.

--- make/autoconf/basics.m4.orig	2019-01-08 09:40:28.000000000 +0000
+++ make/autoconf/basics.m4
@@ -371,7 +371,7 @@ AC_DEFUN([BASIC_REMOVE_SYMBOLIC_LINKS],
       # Resolve file symlinks
       while test $COUNTER -lt 20; do
         ISLINK=`$LS -l $sym_link_dir/$sym_link_file | $GREP '\->' | $SED -e 's/.*-> \(.*\)/\1/'`
-        if test "x$ISLINK" == x; then
+        if test "x$ISLINK" = x; then
           # This is not a symbolic link! We are done!
           break
         fi
@@ -477,7 +477,7 @@ AC_DEFUN([BASIC_SETUP_TOOL],
       # If it failed, the variable was not from the command line. Ignore it,
       # but warn the user (except for BASH, which is always set by the calling BASH).
       if test "x$1" != xBASH; then
-        AC_MSG_WARN([Ignoring value of $1 from the environment. Use command line variables instead.])
+        :
       fi
       # Try to locate tool using the code snippet
       $2
@@ -1227,7 +1227,7 @@ AC_DEFUN([BASIC_CHECK_GREP],
   NEEDLE_SPACES='ccc bbb aaa'
   NEEDLE_LIST=${NEEDLE_SPACES// /$'\n'}
   RESULT="$($GREP -Fvx "$STACK_LIST" <<< "$NEEDLE_LIST")"
-  if test "x$RESULT" == "x"; then
+  if test "x$RESULT" = "x"; then
     AC_MSG_RESULT([yes])
   else
     if test "x$OPENJDK_TARGET_OS" = "xaix"; then
