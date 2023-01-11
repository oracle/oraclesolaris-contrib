# Oracle Solaris OpenJDK Builder

This project builds all OpenJDK versions from 9 till latest 17 for Solaris 11.4.

Note that this was done based on great job of Peter Tribble:
https://ptribble.blogspot.com/2021/12/keeping-java-alive-on-illumos.html

At this time only amd64 platform is expected to work (not SPARC).

You just need to have:
- Oracle Solaris 11.4 (at least S11.4.24) with installed system header files
- Mercurial
- Git
- JDK 8
- GCC 10 (for JDK-13 and above)
- Oracle Solaris Studio 12.4 (for JDK-9, JDK-10, JDK-11, and JDK-12)
- Internet access for OpenJDK repositories

Alternatively you can use your OpenJDK repository mirrors and set them via
environment variables JDK_REPO (for http://hg.openjdk.java.net/jdk-updates)
and JDK_GITHUB_REPO (for JDK_GITHUB_REPO=https://github.com/openjdk).
You will need both.


Example:

```
git clone https://github.com/oracle/oraclesolaris-contrib.git
cd oraclesolaris-contrib/OracleSolaris_OpenJDK_Builder/
./build-all.sh
Building Openjdk 9...
Building Openjdk 10...
Building Openjdk 11...
Building Openjdk 12...
Building Openjdk 13...
Building Openjdk 14...
Building Openjdk 16...
Building Openjdk 17...
```

--

After the build you should inspect build_dir/ for your OpenJDK binaries.

Your build log files will be available in logs/ directory.
