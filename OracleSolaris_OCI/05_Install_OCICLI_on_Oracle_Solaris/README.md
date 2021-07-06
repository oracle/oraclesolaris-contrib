# How to install OCI CLI on Oracle Solaris 

Oracle Cloud Infrastructure (OCI) provides a comprehensive CLI, the *oci* command, written in Python as is true of many recent system tools. The CLI and the underlying Python SDK are very portable, but have some dependencies on other Python modules at particular versions, so can be somewhat complex to install on any particular OS platform. Fortunately, Python has a powerful module known as [virtualenv](https://virtualenv.pypa.io/en/latest/) that makes it fairly simple to install and run a Python application and its dependencies in isolation from other Python programs that may have conflicting requirements. This is especially an issue with modern enterprise operating systems such as Solaris, which use Python for system tools and don't necessarily update all of their modules as quickly as the cloud SDK's require. OCI makes use of virtualenv to provide an easy installation setup for any Unix-like operating system, including [Solaris 11.4](https://www.oracle.com/technetwork/server-storage/solaris11/overview/index.html). There are just a couple of extra things we need to do in order for it to work on Solaris. The first thing to know is whether you're installing on a recent Solaris 11.4 SRU with Python 3.7 installed, as the process is slightly easier. The easiest way to find this out is with the `pkg mediator` command, like so:

```
# pkg mediator python3
MEDIATOR     VER. SRC. VERSION IMPL. SRC. IMPLEMENTATION
python3      system    3.7     system 
```

If the output doesn't show 3.7, you can try installing it with **pkg install runtime/python-37** but most likely this will require you to update to a more recent SRU, as normally Python 3.7 will be installed by default. If you can't do that, then follow the 11.4 GA Instructions section.

### 11.4 SRU Instructions

Step(1): Ensure developer components are installed: **pkg change-facet facet.devel=true**

Step(2): Install the compiler, system headers, pkg-config tool: **pkg install gcc system/header developer/build/pkg-config**

Step(3): Set the correct pkgconfig path in your environment: **export PKG_CONFIG_PATH=/usr/openssl/1.1/pkgconfig/64/:/usr/lib/64/pkgconfig**

Step(4): Set the correct include path in your environment: **export CFLAGS="$(pkg-config --cflags libffi --libs libcrypto libssl)"**

Step(5): Instruct the installer not to build rust: **export CRYPTOGRAPHY_DONT_BUILD_RUST=1**

Step(6): Now follow the installation instructions from the [OCI CLI documentation](https://docs.cloud.oracle.com/iaas/Content/API/SDKDocs/cliinstall.htm)


### 11.4 GA Instructions

Step(1): Install[ Oracle Developer Studio](https://www.oracle.com/technetwork/server-storage/developerstudio/overview/index.html)'s C compiler - any recent version should do, I've tested 12.4, 12.5 and 12.6. Once you've obtained credentials for the package repository and configured the solarisstudio publisher, the command is simply **pkg install --accept developer/developerstudio-126/cc**

Step(2): Ensure the C compiler command is in your path: **PATH=$PATH:/opt/developerstudio12.6/bin**

Step(3): Install the system headers and pkg-config tool. **pkg install system/header developer/build/pkg-config**

Step(4): Set the correct include path in your environment: **export CFLAGS=$(pkg-config --cflags libffi)**

Step(5): Export the config path for OCI to recognize the package

```
export PKG_CONFIG_PATH=/usr/lib/64/pkgconfig:/usr/openssl/1.1/pkgconfig/64/
export CFLAGS="$(pkg-config --cflags libffi --libs libcrypto libssl)"
```

Step(6): Now follow the installation instructions from the [OCI CLI documentation](https://docs.cloud.oracle.com/iaas/Content/API/SDKDocs/cliinstall.htm)

Once you download and execute the basic install script, you'll have to answer several prompts regarding the installation locations for the OCI CLI components, after that it will download a series of dependencies, build and install them to the specified location, this takes just a couple of minutes. I've included a transcript of a session below so you can see what a successful run of the OCI install script looks like. 

```
# bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 17509  100 17509    0     0   102k      0 --:--:-- --:--:-- --:--:--  103k

    ******************************************************************************
    You have started the OCI CLI Installer in interactive mode. If you do not wish
    to run this in interactive mode, please include the --accept-all-defaults option.
    If you have the script locally and would like to know more about
    input options for this script, then you can run:
    ./install.sh -h
    If you would like to know more about input options for this script, refer to:
    https://github.com/oracle/oci-cli/blob/master/scripts/install/README.rst
    ******************************************************************************

Downloading Oracle Cloud Infrastructure CLI install script from https://raw.githubusercontent.com/oracle/oci-cli/v2.22.0/scripts/install/install.py to /tmp/oci_cli_install_tmp_Ywnk.
############################################################################################################### 100.0%
Running install script.
python3 /tmp/oci_cli_install_tmp_Ywnk
-- Verifying Python version.
-- Python version 3.7.9 okay.

===> In what directory would you like to place the install? (leave blank to use '/root/lib/oracle-cli'):
-- Creating directory '/root/lib/oracle-cli'.
-- We will install at '/root/lib/oracle-cli'.

===> In what directory would you like to place the 'oci' executable? (leave blank to use '/root/bin'):
-- Creating directory '/root/bin'.
-- The executable will be in '/root/bin'.

===> In what directory would you like to place the OCI scripts? (leave blank to use '/root/bin/oci-cli-scripts'):
-- Creating directory '/root/bin/oci-cli-scripts'.
-- The scripts will be in '/root/bin/oci-cli-scripts'.

===> Currently supported optional packages are: ['db (will install cx_Oracle)']
What optional CLI packages would you like to be installed (comma separated names; press enter if you don't need any optional packages)?:
-- The optional packages installed will be ''.
-- Trying to use python3 venv.
-- Executing: ['/usr/bin/python3', '-m', 'venv', '/root/lib/oracle-cli']
-- Executing: ['/root/lib/oracle-cli/bin/pip', 'install', '--upgrade', 'pip']
Collecting pip
  Downloading pip-21.1.2-py3-none-any.whl (1.5 MB)
     |████████████████████████████████| 1.5 MB 20.0 MB/s
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 20.1.1
    Uninstalling pip-20.1.1:
      Successfully uninstalled pip-20.1.1
Successfully installed pip-21.1.2
-- Executing: ['/root/lib/oracle-cli/bin/pip', 'install', '--cache-dir', '/tmp/tmpcjvkhcwi', 'wheel', '--upgrade']
Collecting wheel
  Downloading wheel-0.36.2-py2.py3-none-any.whl (35 kB)
Installing collected packages: wheel
Successfully installed wheel-0.36.2
-- Executing: ['/root/lib/oracle-cli/bin/pip', 'install', '--cache-dir', '/tmp/tmpcjvkhcwi', 'oci_cli', '--upgrade']
Collecting oci_cli
  Downloading oci_cli-2.25.4-py2.py3-none-any.whl (19.2 MB)
     |████████████████████████████████| 19.2 MB 17.3 MB/s
Collecting retrying==1.3.3
  Downloading retrying-1.3.3.tar.gz (10 kB)
Collecting pyOpenSSL==19.1.0
  Downloading pyOpenSSL-19.1.0-py2.py3-none-any.whl (53 kB)
     |████████████████████████████████| 53 kB 7.9 MB/s
Collecting oci==2.40.1
  Downloading oci-2.40.1-py2.py3-none-any.whl (9.5 MB)
     |████████████████████████████████| 9.5 MB 9.7 MB/s
Collecting pytz>=2016.10
  Downloading pytz-2021.1-py2.py3-none-any.whl (510 kB)
     |████████████████████████████████| 510 kB 27.7 MB/s
Collecting jmespath==0.10.0
  Downloading jmespath-0.10.0-py2.py3-none-any.whl (24 kB)
Collecting click==6.7
  Downloading click-6.7-py2.py3-none-any.whl (71 kB)
     |████████████████████████████████| 71 kB 23.5 MB/s
Collecting six==1.14.0
  Downloading six-1.14.0-py2.py3-none-any.whl (10 kB)
Collecting arrow==0.17.0
  Downloading arrow-0.17.0-py2.py3-none-any.whl (50 kB)
     |████████████████████████████████| 50 kB 12.2 MB/s
Collecting cryptography<=3.4.7,>=3.2.1
  Downloading cryptography-3.4.7.tar.gz (546 kB)
     |████████████████████████████████| 546 kB 32.7 MB/s
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
    Preparing wheel metadata ... done
Collecting PyYAML<6,>=5.4
  Downloading PyYAML-5.4.1.tar.gz (175 kB)
     |████████████████████████████████| 175 kB 13.7 MB/s
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
    Preparing wheel metadata ... done
Collecting certifi
  Downloading certifi-2021.5.30-py2.py3-none-any.whl (145 kB)
     |████████████████████████████████| 145 kB 39.1 MB/s
Collecting configparser==4.0.2
  Downloading configparser-4.0.2-py2.py3-none-any.whl (22 kB)
Collecting terminaltables==3.1.0
  Downloading terminaltables-3.1.0.tar.gz (12 kB)
Collecting python-dateutil<3.0.0,>=2.5.3
  Downloading python_dateutil-2.8.1-py2.py3-none-any.whl (227 kB)
     |████████████████████████████████| 227 kB 7.6 MB/s
Collecting cffi>=1.12
  Downloading cffi-1.14.5.tar.gz (475 kB)
     |████████████████████████████████| 475 kB 12.5 MB/s
Collecting pycparser
  Downloading pycparser-2.20-py2.py3-none-any.whl (112 kB)
     |████████████████████████████████| 112 kB 35.3 MB/s
Building wheels for collected packages: retrying, terminaltables, cryptography, cffi, PyYAML
  Building wheel for retrying (setup.py) ... done
  Created wheel for retrying: filename=retrying-1.3.3-py3-none-any.whl size=11429 sha256=0bebf3fee927a686852b4fa073d1d98f466cb51bc955abb883ad75c4e1780593
  Stored in directory: /tmp/tmpcjvkhcwi/wheels/f9/8d/8d/f6af3f7f9eea3553bc2fe6d53e4b287dad18b06a861ac56ddf
  Building wheel for terminaltables (setup.py) ... done
  Created wheel for terminaltables: filename=terminaltables-3.1.0-py3-none-any.whl size=15355 sha256=9e8b8668d0317090e19f0c3a53f7636b378dfd4a45d604f3c251d3a17b767220
  Stored in directory: /tmp/tmpcjvkhcwi/wheels/ba/ad/c8/2d98360791161cd3db6daf6b5e730f34021fc9367d5879f497
  Building wheel for cryptography (PEP 517) ... done
  Created wheel for cryptography: filename=cryptography-3.4.7-cp37-cp37m-solaris_2_11_i86pc_64bit.whl size=830555 sha256=3071c821aa904b0e4c30b14ef9349c45e48de5ebc209fbd0beee34ef999cbcff
  Stored in directory: /tmp/tmpcjvkhcwi/wheels/0f/d4/8b/207901c6ba23c69e3823daeebe87ffc684f28662da0c29bb39
  Building wheel for cffi (setup.py) ... done
  Created wheel for cffi: filename=cffi-1.14.5-cp37-cp37m-solaris_2_11_i86pc_64bit.whl size=365826 sha256=8152a0e7ad8dbb89ee693799525b202d1ae9d15c47bfb567107d25b59dcb2f09
  Stored in directory: /tmp/tmpcjvkhcwi/wheels/be/ae/46/d5dd8377599ae67bfaada5364712144e1146b2f04d20e60f56
  Building wheel for PyYAML (PEP 517) ... done
  Created wheel for PyYAML: filename=PyYAML-5.4.1-cp37-cp37m-solaris_2_11_i86pc_64bit.whl size=45668 sha256=4eeaf77a4ba26a6c09830f9f9b27056d690f1a137bfc0e8078c79bc86574a387
  Stored in directory: /tmp/tmpcjvkhcwi/wheels/f4/51/cc/858604f7bb9cab887106ff266a541546ad783b4fa20875051d
Successfully built retrying terminaltables cryptography cffi PyYAML
Installing collected packages: pycparser, cffi, six, cryptography, pytz, python-dateutil, pyOpenSSL, configparser, certifi, terminaltables, retrying, PyYAML, oci, jmespath, click, arrow, oci-cli
Successfully installed PyYAML-5.4.1 arrow-0.17.0 certifi-2021.5.30 cffi-1.14.5 click-6.7 configparser-4.0.2 cryptography-3.4.7 jmespath-0.10.0 oci-2.40.1 oci-cli-2.25.4 pyOpenSSL-19.1.0 pycparser-2.20 python-dateutil-2.8.1 pytz-2021.1 retrying-1.3.3 six-1.14.0 terminaltables-3.1.0

===> Modify profile to update your $PATH and enable shell/tab completion now? (Y/n): Y

===> Enter a path to an rc file to update (file will be created if it does not exist) (leave blank to use '/root/.bashrc'):
-- Backed up '/root/.bashrc' to '/root/.bashrc.backup'
-- Tab completion set up complete.

-- If tab completion is not activated, verify that '/root/.bashrc' is sourced by your shell.
--

-- ** Run `exec -l $SHELL` to restart your shell. **
--

-- Installation successful.
-- Run the CLI with /root/bin/oci --help
```





Copyright (c) 2021, Oracle and/or its affiliates. Licensed under the Universal Permissive License v 1.0 as shown at [https://oss.oracle.com/licenses/upl/](https://oss.oracle.com/licenses/upl/). 