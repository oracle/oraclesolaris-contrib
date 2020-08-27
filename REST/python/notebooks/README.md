# Using Jupyter Notebooks

This directory contains a set of Jupyter Notebooks that show how to use the Oracle Solaris REST API. The REST API is layered on top of the [Oracle Solaris Remote Administration Daemon (RAD)](https://docs.oracle.com/cd/E37838_01/html/E68270/index.html) which allows remote and local management access to the system. Managing the various parts of Oracle Solaris is done through corresponding RAD modules. By layering the REST API on top of RAD anyone using this REST API can directly use all of the functionality in these RAD modules.

In the featured Jupyter notebooks we're making use of the Python `requests` module to talk to the REST API in Oracle Solaris. Where the intent is to show how using the `requests` module you can access the various parts of the RAD module and how to use them.

One of the benefits of using Python and Jupyter notebooks is that the behavior of the REST API and the RAD modules can be easily translated to other tools using REST to talk to the Oracle Solaris instance. 

Note that every Oracle Solaris Zone and Logical Domain has its own RAD/REST interface which can be independently turned on and accessed. 

Some resources to get started:

- [How to install Jupyter](https://jupyter.org/install)
- [How to turn remote connection on](Settinguptheconnection.md)

