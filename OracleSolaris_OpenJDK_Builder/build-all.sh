#!/bin/bash

WS="`pwd`"
LOG_DIR="$WS/logs"
rm -rf $LOG_DIR
mkdir -p $LOG_DIR

for VERSION in {9..18}; do
  echo "Building Openjdk $VERSION..."
  bash $WS/jdk-$VERSION.sh > $LOG_DIR/jdk-$VERSION.log 2>&1

  # Check for expected sucesful build output.
  tail -1 $LOG_DIR/jdk-$VERSION.log \
    | grep "Finished building target \'bundles\' in configuration " > /dev/null
  if [ $? -ne 0 ] ; then
    echo "Build error. See: $LOG_DIR/jdk-$VERSION.log"
    exit 1
  fi
done
