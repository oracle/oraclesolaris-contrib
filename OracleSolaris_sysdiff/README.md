# Oracle Solaris `sysdiff`

## Overview

Migrating a workload from [Oracle Solaris
10](https://www.oracle.com/solaris/solaris10/downloads/solaris10-get-jsp-downloads.html)
to [Oracle Solaris 11.4](https://www.oracle.com/solaris/solaris11/) can be
challenging. Because of the move from SVR4 packaging to IPS packaging with the
introduction of Oracle Solaris 11, a direct update has not been a possibility.
So even though the [Binary Compatibility
Guarantee](https://www.oracle.com/a/ocom/docs/solaris-guarantee-program-1426902.pdf)
makes it possible to move the application from Oracle Solaris 10 and run it on
Oracle Solaris 11, there are no tools to assist with the move. And knowing what
files to move and how to configure it can be a challenge, especially for older
applications. 

One of the options Oracle Solaris has had was to take a full backup of the
Oracle Solaris 10 image and run it on top of Oracle Solaris 11.4 in a
[`solaris10`](https://docs.oracle.com/cd/E37838_01/html/E88845/index.html)
branded zone, also known as an Oracle Solaris 10 Container. This helps move the
application off of the old system onto the new one, but it does not help
actually making the full move to Oracle Solaris 11. `sysdiff` hopes to solve
this.

## How does `sysdiff` work?

`sysdiff` is intended to bridge the gap from running the application in the
`solaris10` branded zone to running it on Oracle Solaris 11.4 proper. It
contains a `sysdiff` script that inspects the `solaris10` branded zone that
holds the application, and then creates an IPS package from non-OS files found
inside the zone.  It is designed to be run from the Oracle Solaris 11.4 Global
Zone and access the `solaris10` branded zone root filesystem directly.

**`sysdiff` can not work on a standalone Oracle Solaris 10 deployment, such a
system must be first migrated to a `solaris10` branded zone on Solaris 11.4.**

The minimum supported OS version is Oracle Solaris 11.4 SRU21 and the
`solaris10` branded zone must be in the `installed` state.

## How to use `sysdiff`?

`sysdiff` generates a directory referred to as `results-dir` further in this
document. It is absolutely essential that both the source `solaris10` branded
zone and the final version of the `results-dir` are preserved for the lifetime
of the transitioned application.  The reason is that the generated package may
have dependencies on packages which will get obsoleted and removed from Solaris
11.4, and the package will have to be regenerated based on these resources. File
`executionExample` contains sample of such an issue and steps needed to resolve
it.

**Note that transferring binaries built for Solaris 10 (or older) to a Solaris
11.4 [`solaris(7)`](https://docs.oracle.com/cd/E37838_01/html/E61039/index.html)
branded (aka native) zone should be considered a last resort approach.  It is
always preferable to deploy application version dedicated for Solaris 11, and
migrate the Solaris 10 deployment via supported means.**

The sysdiff command requires a subcommand to be specified. The only common
option is `-q`, which silences the non-essential output (e.g. the IPS commands
being executed). All of the subcommands have their own help provided under the
`-h` option.

```
# sysdiff.py -h
usage: sysdiff.py [-h] [-q] {diff,depresolve,lint,publish,archive} ...

Produce a diff between current Solaris 10 branded zone contents and the state
based on the SVR4 packaging data and optionally package them in an IPS
package.

positional arguments:
  {diff,depresolve,lint,publish,archive}

optional arguments:
  -h, --help            show this help message and exit
  -q                    suppress informational output
```

The first step to analyze a new Solaris 10 branded zone is `sysdiff diff`.

Running `sysdiff diff` analyses an Solaris 10 branded zone root filesystem, and produces
a list of new and modified files encountered in the zone. For details about
this step inner workings please see the `README.implementation` file.

```
# sysdiff.py diff -h
usage: sysdiff.py diff [-h] [-c] [-f] [-l] [--exclude-dirs-path EXCLUDE_DIRS]
                       [--extra-ignore-dirs IGNORE]
                       [--results-dir-parent OUTPUT_DIR] [--pkg-name PKG_NAME]
                       [--pkg-version PKG_VERSION] [--pkg-summary PKG_SUMMARY]
                       [--pkg-desc PKG_DESC] [--preserve-age PRESERVE_AGE]
                       zonename

Produce a diff between current Solaris 10 branded zone contents and the state
based on the SVR4 packaging data.

positional arguments:
  zonename              name of the target zone (must be Solaris 10 branded
                        zone)

optional arguments:
  -h, --help            show this help message and exit
  -c                    enable checksums for all files (slow)
  -f                    ignore the known new/modified files
  -l                    output plain file list, not IPS manifest
  --exclude-dirs-path EXCLUDE_DIRS
                        location of the file from which the directories to be
                        excluded from search are to be read. By default
                        /net/ons-0/public/kkarczew/sysdiff/excludeDirs
  --extra-ignore-dirs IGNORE
                        comma separated list of directories to be ignored
                        during scan appended to the list read from
                        "excludeDirs"
  --results-dir-parent OUTPUT_DIR
                        directory where the results directory will be created,
                        by default "/var/tmp" will be used
  --pkg-name PKG_NAME   name of the generated package
  --pkg-version PKG_VERSION
                        version of the generated package
  --pkg-summary PKG_SUMMARY
                        short info about the generated package
  --pkg-desc PKG_DESC   long description of the generated package
  --preserve-age PRESERVE_AGE
                        number of days to be used as threshold for the
                        "preserve" heuristic. "0" disables the mechanism,
                        default is 5
```

By default the `sysdiff diff` does not check checksums of files which passed all
the earlier checks against the SVR4 database (including size and timestamp
verification). Testing has proven these checks are unlikely to find new
mismatches - if both size and timestamp matches, it would require malicious
tampering to provide different content of the file. Option `-c` enables running
checksum tests for all the files. Please keep in mind that this can cause the
script to require several hours to analyze a single zone.

`sysdiff` is accompanied by lists of files which are detected as *new* or
*modified* in a freshly deployed zone. These files are by default filtered out
from the output, to ease analysis of the generated manifest.  If this approach
is deemed undesirable, `-f` option disables it. It is also supported to adjust
the bundled lists by adding or removing entries in the provided lists.

Similarly the script excludes certain directories (read from `excludeDirs` file
by default) from the scan altogether. The list of excluded dirs can be modified
in the file, or extended via the `--extra-ignore-dirs` option. It is also
possible to provide alternative file of directories to be excluded via the
`--exclude-dirs-path` option. Please note that the hardlink detection feature
(essential for proper packaging) may be affected by excluding too many
directories (namely those containing some of the hardlinks for given file).

The `-l` option switches the generated output from IPS manifest to plain file
lists.

The results of the script will be generated in a directory, which by default
will be created in `/var/tmp`. This location can be adjusted via the
`--results-dir-parent` option. 

The `pkg-*` options are used to set the equivalent options in the IPS manifest.
These might be adjusted in the manifest by hand if necessary, `sysdiff` never
reads them from the manifest. The `pkg-fmri` (constructed from `pkg-name` and
`pkg-version`) is preserved in the `params.ini` and used by the `sysdiff
archive` command.

The `sysdiff diff` script attempts to determine which of the found new files
should be treated as modifiable by the user, or changing in the lifetime of the
application (e.g. config files, logs, data files). The heuristics used to
determine that is based on the last modification date - by default files
modified less than 5 days ago are tagged with `preserve` option in the manifest.
`--preserve-age` option allows to change that time, or disable this feature
completely by passing `0`. Please keep in mind that the heuristic is likely
inadequate for config files, which were set up when the application was first
deployed, and never needed an adjustment, but it is impossible to offer a better
guess in such cases.

Once the `sysdiff diff` generates the IPS manifest it is crucial to review it,
remove false positives not eliminated by the file lists provided, and assess
which files should be preserved during future updates by assigning `preserve`
tag to their entries. The manifest is generated in `results-dir` in the file
`<pkg-name>.p5m`, where the `pkg-name` is the zone name by default unless set
explicitly via the `--pkg-name` option.

The manifests may contain comments detailing minor issues encountered during
manifest generation, e.g. if it was not possible to convert UID/GID to
user/group name the comment will mention it, and it is necessary to expand the
entry with a `owner=/group=` attribute, otherwise the next step will fail.

Generally speaking after each modification of the manifest file all the further
steps of the process need to be re-run, starting with `sysdiff depresolve`.

The `sysdiff depresolve` is a thin wrapper over the `pkgdepend(1) generate` and
`pkgdepend(1) resolve` IPS commands. It pulls the relevant information from the
results directory and command line options and transforms them into `pkgdepend`
arguments.  This command may find issues with the manifest prepared by `sysdiff
diff` and hand-adjusted. These issues have to be resolved before next steps of
the process.

```
# sysdiff.py depresolve -h
usage: sysdiff.py depresolve [-h] results-dir

Resolve the dependencies for the package manifest.
Wrapper for the 'pkgdepend' command

positional arguments:
  results-dir  directory where results of 'sysdiff diff' were stored

optional arguments:
  -h, --help   show this help message and exit
```

The dependencies generated by `pkgdepend resolve` will list pkg FMRIs with the
latest available version. This will prevent the generated package from being
installed on an older system, but will not prevent OS update, as these are
treated as minimum version needed to satisfy the dependency. If needed these
FMRIs might be stripped down to package name, with the caveat that older
version of the package might not satisfy the dependency as expected.

It is possible that `sysdiff depresolve` will uncover dependencies (e.g.
libraries), which cannot be satisfied within Oracle Solaris 11.4, as they were
either replaced by new, incompatible versions, or are no longer delivered for
various reasons. Such dependencies might be satisfied by bundling Solaris 10
versions of the libraries, by including them in the manifest by hand, but such
an approach carries serious security implications, as the bundled binary will
not receive security fixes anymore, neither from the Solaris 10 patches nor
Solaris 11.4 SRUs. If bundling a Solaris 10 binary is absolutely necessary, the
package will have to be refreshed every time the bundled binary is patched in
Solaris 10. It might be a good idea to split these binaries into a separate
package for ease of maintenance.

Please keep in mind that Solaris 10 may contain unsupported FOSS software
which carries additional security risks. Packaging such a software is highly
discouraged. Knowledge article [ID
1400676.1](https://support.oracle.com/knowledge/Sun%20Microsystems/1400676_1.html)
contains the list of no longer supported FOSS components in Oracle Solaris.

The `sysdiff lint` is a thin wrapper over the `pkglint(1)` IPS command.
It pulls the relevant information from the results directory and command line
options and transforms them into `pkglint` arguments. `pkglint` runs detailed
analysis on the manifest detecting all manners of issues. Errors emitted by
this command have to be assessed and addressed before running next steps of
the process.

```
# sysdiff.py lint -h
usage: sysdiff.py lint [-h] --s11.4-repo REPO [--cache-dir CACHE_DIR]
                       results-dir

Validate the manifest before packaging.
Wrapper for the 'pkglint' command

positional arguments:
  results-dir           directory where results of 'sysdiff diff' were stored

optional arguments:
  -h, --help            show this help message and exit
  --s11.4-repo REPO     Solaris 11.4 repo URI
  --cache-dir CACHE_DIR
                        cache dir location
```

`pkglint` requires access to Solaris 11.4 repository to work properly, it
must be supplied to the `sysdiff lint` command via the `--s11.4-repo` option.

The repository will be cached in the cache dir, which may be reused for future
pkglint runs - it's not affected by the command. The default is to use
`<results-dir>.cache` directory, it can be adjusted via the `--cache-dir`
option. The cache directory can be removed once the package is built, it is
not necessary to preserve it for future package regeneration.

lint warnings can be ignored if they are assessed to not be a concern, errors
denote issues which will prevent a valid package from being created. The
`executionExample` contains some examples of lint output and suggestions how
to deal with them.

The `sysdiff publish` is a thin wrapper over the 'pkgsend(1) publish' IPS
command. It pulls the relevant information from the results directory and
command line options and transforms them into 'pkgsend publish' arguments.

```
# sysdiff.py publish -h
usage: sysdiff.py publish [-h] [-c] --target-repo REPO [--publisher PUBLISHER]
                          results-dir

Publish the package based on the prepared manifest.
Wrapper for the 'pkgsend publish' command

positional arguments:
  results-dir           directory where results of 'sysdiff diff' were stored

optional arguments:
  -h, --help            show this help message and exit
  -c                    create a file system based repository for the package
  --target-repo REPO    target repo URI
  --publisher PUBLISHER
                        publisher prefix for the repo
```

The `sysdiff publish` command publishes the package based on the manifest
processed by the earlier steps into the provided target repository. It can
utilize an existing repository, or create one from scratch when the `-c` flag
is provided. In such case the publisher string needs to be provided as well,
via the `--publisher` option.

Every time a package is published a timestamp is appended to the FMRI, so new
package is created. If a new version with incremented version number is
desirable, the pkg-fmri entry in the manifest needs to be updated by hand.

The `sysdiff archive` is a thin wrapper over the `pkgrecv(1) -a` IPS
command. It pulls the relevant information from the results directory and
command line options and transforms them into `pkgrecv -a` arguments.
This step is optional - the package may be installed directly from the repo
created in previous step, but packaging it in the archive might be convenient
in some cases.

```
# sysdiff.py archive -h
usage: sysdiff.py archive [-h] --source-repo REPO [--archive ARCHIVE]
                          [--pkg-fmri PKG_FMRI]
                          results-dir

Generate an archive from the published package.
Wrapper for the 'pkgrecv -a' command

positional arguments:
  results-dir          directory where results of 'sysdiff diff' were stored

optional arguments:
  -h, --help           show this help message and exit
  --source-repo REPO   pkg repo URI (the same as used for the publish command)
  --archive ARCHIVE    archive name
  --pkg-fmri PKG_FMRI  FMRI of the package to be archived
```

`--source-repo` points to the directory where the package was published in
the previous step.

The `--archive` option allows to change the default archive location, which is
the same as package manifest, with the extension changed to `p5p`.

The `--pkg-fmri` option allows to specify the FMRI of the package to be
archived, by default it is read from the `params.ini` file.

## Why on GitHub?

`sysdiff` is currently not part of Oracle Solaris, we are looking for feedback
on how we can improve it and if it helps solve the migration challenges. And
based on user feedback it may be integrated into a future Oracle Solaris 11.4
SRU. 

The `sysdiff` tool and all its related files in the GitHub
`oracle/oraclesolaris-contrib/OracleSolaris_sysdiff` repository come with no
warranty. It is not a commitment to deliver any material, code, or
functionality, and should not be relied upon in making purchasing decisions. The
development, release, and timing of any `sysdiff` features or functionality
described here remains at the sole discretion of Oracle.

Copyright (c) 2022, Oracle and/or its affiliates. Licensed under the Universal
Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.
