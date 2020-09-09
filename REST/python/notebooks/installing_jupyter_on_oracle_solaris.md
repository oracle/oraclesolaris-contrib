# How to Install Jupyter on Oracle Solaris

For those who want to install Jupyter on Oracle Solaris (both on SPARC and x86) it's slightly more work than on other platforms. This is mainly due to the need to build your own ZeroMQ, all the other components which are mostly Python based get pulled in, and if necessary, built by `pip`.

**Note:** When doing this we highly recommend you use either `virtualenv` or `pipenv` to create Python virtual enviroments with their own version of Python and packages separate from the main system delivered Python installation. This way you won't disrupt any Oracle Solaris services that use Python.

## Building ZeroMQ

The first step is to install and build ZeroMQ a.k.a. 0MQ. This needs to be pulled from it's [GitHub page](https://github.com/zeromq/libzmq) and compiled. But before we can do this we need to add a bunch of packages with the bits needed to do this. 

### Installing Packages

The packages you'll need to install are mainly for pulling 0MQ in (with `git`), and to compile it. Note you'll need to use `gcc` and not the Studio compiler, so even though we're installing the Studio tools it's actually `gcc` that we're using to compile it:

```bash
root@demo-jupyter:~# pkg install --accept autoconf automake pkg-config libtool developerstudio-126 gnu-make gcc git
------------------------------------------------------------
Package: pkg://solarisstudio/developer/developerstudio-126/studio-legal@12.6-1.0.0.1:20170815T160721Z
License: devpro.OTN.license

You acknowledge that your use of Oracle Developer Studio is subject to the Oracle Developer Studio OTN License Agreement.  The OTN License Agreement is located at : http://www.oracle.com/technetwork/licenses/studio-license-2980206.html




           Packages to install: 55
           Mediators to change:  2
            Services to change:  1
       Create boot environment: No
Create backup boot environment: No

DOWNLOAD                                PKGS         FILES    XFER (MB)   SPEED
Completed                              55/55   13667/13667  993.2/993.2 24.1M/s

PHASE                                          ITEMS
Installing new actions                   22960/22960
Updating package state database                 Done 
Updating package cache                           0/0 
Updating image state                            Done 
Creating fast lookup database                   Done 
Updating package cache                           3/3 
```

**Note 1:** You'll probably have to do this step as a privileged user to be able to install these packages. The example above is doing this as user `root` in a test zone, but this could aslo be a regular user that has the *Software Installation* profile added. See [profiles(1)](https://docs.oracle.com/cd/E88353_01/html/E37839/profiles-1.html#REFMAN1profiles-1) for more info.

**Note 2:** To install Studio you've probably need add the [external Studio publisher](https://pkg-register.oracle.com/register/repos/) to IPS or to download the Studio IPS packages separately, for example from [OTN](https://www.oracle.com/tools/developerstudio/downloads/developer-studio-jsp.html) or My Oracle Support.

### Choosing a Location

Before pulling the bits in it may be useful to either create a new ZFS filesytem, either in the rpool or another zpool you've mounted for this type of data. This will make it easier to manage it separately, for example if you want to create a snapshot. 

In general on Oracle Solaris these types of things would be expected to be installed in `/opt`, but some folks use `/usr/local` or `/data` as a location. 

 In this example we're only creating a directory, still as user `root`, in `/opt`:

```bash
root@demo-jupyter:~# mkdir /opt/zeromq
```

### Downloading 0MQ and Building it

Now we download 0MQ from from its project GitHub page:

```bash
root@demo-jupyter:~# cd /opt/zeromq
root@demo-jupyter:/opt/zeromq# git clone https://github.com/zeromq/libzmq
Cloning into 'libzmq'...
remote: Enumerating objects: 42728, done.
remote: Total 42728 (delta 0), reused 0 (delta 0), pack-reused 42728
Receiving objects: 100% (42728/42728), 21.24 MiB | 1.68 MiB/s, done.
Resolving deltas: 100% (31224/31224), done.
```

Now we can go ahead and build 0MQ:

```bash
root@demo-jupyter:/opt/zeromq# cd libzmq/
root@demo-jupyter:/opt/zeromq/libzmq# ./autogen.sh && ./configure MAKE="gmake" && gmake && gmake install
autoreconf: Entering directory `.'
autoreconf: configure.ac: not using Gettext
autoreconf: running: aclocal -I config --force -I config
autoreconf: configure.ac: tracing
autoreconf: running: libtoolize --copy --force

...

libtool: install: /usr/bin/ginstall -c tools/.libs/curve_keygen /usr/local/bin/curve_keygen
 /usr/bin/gmkdir -p '/usr/local/include'
 /usr/bin/ginstall -c -m 644 include/zmq.h include/zmq_utils.h '/usr/local/include'
 /usr/bin/gmkdir -p '/usr/local/lib/pkgconfig'
 /usr/bin/ginstall -c -m 644 src/libzmq.pc '/usr/local/lib/pkgconfig'
gmake[2]: Leaving directory '/opt/zeromq/libzmq'
gmake[1]: Leaving directory '/opt/zeromq/libzmq'
```

At this point 0MQ is installed on your system.

A final not, for those that want to do this at scale check out [Martin's Blog on creating an IPS package](https://blogs.oracle.com/solaris/solaris-ips-on-steroids%3a-building-foss-on-demand). His code is actually using 0MQ as the example. When you create a package and add it to your repo you can easily roll this out to many systems.

## Using `pipenv` or `virtualenv` to Install Jupyter

Now on to the actual install of Jupyter. As said above it's highly recommended to first create a Python virtual environment with either `pipenv` or `virtualenv` before you start adding more Python software. In this example we'll show using `virtualenv`.

First we shift to the user we want to run Jupyter as, this shouldn't be user `root`. And we create a directory `projects` to hold our Python 3 and Jupyter binaries:

```bash
root@demo-jupyter:/opt/zeromq/libzmq# su - demo
Oracle Corporation      SunOS 5.11      11.4    November 2019
demo@demo-jupyter:~$ mkdir projects
demo@demo-jupyter:~$ cd projects
```

Next we create the new `virtualenv` and set some environment variables to ensure `gcc` is found and the 64 bit libraries are used:

```bash
demo@demo-jupyter:~/projects$ export PKG_CONFIG_PATH=/usr/lib/64/pkgconfig
demo@demo-jupyter:~/projects$ export PATH=$PATH:/opt/developerstudio12.6/bin
```

Now we can activate the `virtualenv` and pull Jupyter and all it's dependencies:

```bash
demo@demo-jupyter:~/projects$ source jupyter-env/bin/activate
(jupyter-env) demo@demo-jupyter:~/projects$ pip install jupyterlab
Collecting jupyterlab
  Downloading https://files.pythonhosted.org/packages/0c/2e/1bea5f1cb8ebb2db6e0b05887fa8a4f4e8f253ca20e139e7997e80196c3b/jupyterlab-2.2.6-py3-none-any.whl (7.8MB)
    100% |████████████████████████████████| 7.8MB 4.1MB/s 
Collecting notebook>=4.3.1 (from jupyterlab)
  Downloading https://files.pythonhosted.org/packages/ea/00/1be79c61e2dfedb29c430b0e08f9fd2cb6ee4f6be92ba6f185dd6bb00052/notebook-6.1.3-py3-none-any.whl (9.4MB)
    100% |████████████████████████████████| 9.4MB 6.1MB/s 

...

Installing collected packages: tornado, pyzmq, ipython-genutils, traitlets, ptyprocess, terminado, six, python-dateutil, jupyter-core, jupyter-client, parso, jedi, decorator, backcall, wcwidth, prompt-toolkit, pickleshare, pexpect, pygments, ipython, ipykernel, Send2Trash, prometheus-client, zipp, importlib-metadata, pyrsistent, attrs, jsonschema, nbformat, defusedxml, MarkupSafe, jinja2, mistune, webencodings, pyparsing, packaging, bleach, pandocfilters, testpath, entrypoints, nbconvert, pycparser, cffi, argon2-cffi, notebook, json5, urllib3, idna, certifi, chardet, requests, jupyterlab-server, jupyterlab
  Running setup.py install for tornado ... done
  Running setup.py install for pyzmq ... done
  Running setup.py install for pyrsistent ... done
  Running setup.py install for MarkupSafe ... done
  Running setup.py install for pandocfilters ... done
  Running setup.py install for cffi ... done
Successfully installed MarkupSafe-1.1.1 Send2Trash-1.5.0 argon2-cffi-20.1.0 attrs-20.2.0 backcall-0.2.0 bleach-3.1.5 certifi-2020.6.20 cffi-1.14.2 chardet-3.0.4 decorator-4.4.2 defusedxml-0.6.0 entrypoints-0.3 idna-2.10 importlib-metadata-1.7.0 ipykernel-5.3.4 ipython-7.18.1 ipython-genutils-0.2.0 jedi-0.17.2 jinja2-2.11.2 json5-0.9.5 jsonschema-3.2.0 jupyter-client-6.1.7 jupyter-core-4.6.3 jupyterlab-2.2.6 jupyterlab-server-1.2.0 mistune-0.8.4 nbconvert-5.6.1 nbformat-5.0.7 notebook-6.1.3 packaging-20.4 pandocfilters-1.4.2 parso-0.7.1 pexpect-4.8.0 pickleshare-0.7.5 prometheus-client-0.8.0 prompt-toolkit-3.0.7 ptyprocess-0.6.0 pycparser-2.20 pygments-2.6.1 pyparsing-2.4.7 pyrsistent-0.16.0 python-dateutil-2.8.1 pyzmq-19.0.2 requests-2.24.0 six-1.15.0 terminado-0.8.3 testpath-0.4.4 tornado-6.0.4 traitlets-5.0.4 urllib3-1.25.10 wcwidth-0.2.5 webencodings-0.5.1 zipp-3.1.0
```

At this point Jupyter is fully installed on the system and ready to go if you're going to connect to it locally through the browser in the same system.

You can now start Jupyter:

```bash
(jupyter-env) demo@demo-jupyter:~/projects$ mkdir notebooks
(jupyter-env) demo@demo-jupyter:~/projects$ cd notebooks
(jupyter-env) demo@demo-jupyter:~/projects/notebooks$ jupyter notebook
[I 08:15:43.583 NotebookApp] JupyterLab extension loaded from /export/home/demo/projects/jupyter-env/lib/python3.7/site-packages/jupyterlab
[I 08:15:43.583 NotebookApp] JupyterLab application directory is /export/home/demo/projects/jupyter-env/share/jupyter/lab
[I 08:15:43.589 NotebookApp] Serving notebooks from local directory: /export/home/demo/projects/notebooks
[I 08:15:43.589 NotebookApp] Jupyter Notebook 6.1.3 is running at:
[I 08:15:43.589 NotebookApp] https://demo-jupyter:8888/
[I 08:15:43.589 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).

...
```

## Allowing Remote Connection to Jupyter

If you want to connect to it remotely can do this multiple ways. One is start Jupyter with the `--no-browser` option and then ssh to the system forwarding a local port to the port on the remote system. Some thing like:

```
jupyter notebook --no-browser --port=8889
```

and then:

```
ssh -N -f -L localhost:8888:localhost:8889 username@your_remote_host_name
```

Now Jupyter should be available at `localhost:8888` in your browser.

The other way is to actually make the Jupyter web service available for external connections. To do this you'll need to do some extra steps to configure it to listen to its external IP address(es) and to set up a secure link and website password. For course you want to be careful to do this on networks you don't trust. For additional information see the [Jupyter docs on running a notebook server](https://jupyter-notebook.readthedocs.io/en/stable/public_server.html).

Here are the steps in short. First we generate a config file:

```bash
(jupyter-env) demo@demo-jupyter:~/projects$ jupyter notebook --generate-config
Writing default config to: /export/home/demo/.jupyter/jupyter_notebook_config.py
```

Then in this file find:

```
# c.NotebookApp.open_browser = True
```

Uncomment it and set it to `False`:

```
c.NotebookApp.open_browser = False
```

Now find:

```
# c.NotebookApp.ip = 'localhost'
```

Uncomment it and set it to `'*'`:

```
c.NotebookApp.ip = '*'
```

If you start Jupyter now it will already allow you connect but you probably want to also make it ask for a password and use TLS.

To set the password run:

```bash
(jupyter-env) demo@demo-jupyter:~/projects$ jupyter notebook password
Enter password: 
Verify password: 
[NotebookPasswordApp] Wrote hashed password to /export/home/demo/.jupyter/jupyter_notebook_config.json
```

The Jupyter docs mentioned above also show other ways of setting this.

Now t oconfigure the use of TLS. In the `~/.jupyter/jupyter_notebook_config.py` file look for `# c.NotebookApp.certfile = ''` and `# c.NotebookApp.keyfile = ''` and point them to your local certificates:

```
c.NotebookApp.certfile = '/export/home/demo/.jupyter/host.crt'
```

and

```
c.NotebookApp.keyfile = '/export/home/demo/.jupyter/host.key'
```

Of course if these certificates aren't signed by a *managed CA* the browser will probably complain and you'll have to accept this or use the key file. For more info on managed CA's see the [README on certificates](certs/README.md).

 Once you've made these changes you can start Jupyter as described above and you can now remotely access Jupyter over HTTPS, and you'll be asked for the password you set up.

## Adding the New Python Kernel to Jupyter

A final note on using Jupyter and `pipenv` or `virtualenv` environments, it could be that you'd like to create one environment to install and run Jupyter, but at the same time have another environment for your code. For example because the version of Python needed for Jupyter and it's elements is different than the version needed for you code. To solve for this case Jupyter allows you to define multiple `kernels` which you can switch your notebook to. 

The way to manage, add, delete these kernels is with the `jupyter kernelspec` command. So for example this is how you look at the defined kernels:

```
jupyter kernelspec list
```

and if you want to add a kernel you run this from within your virtual environment:

```
jupyter kernelspec install --user --name=<my_name>
```

This should then give you an extra kernel option to switch to within the running notebook.

Copyright (c) 2020, Oracle and/or its affiliates. Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.