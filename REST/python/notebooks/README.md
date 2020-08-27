# Using Jupyter Notebooks

This directory contains a set of Jupyter Notebooks that show how to use the Oracle Solaris REST API. The REST API is layered on top of the [Oracle Solaris Remote Administration Daemon (RAD)](https://docs.oracle.com/cd/E37838_01/html/E68270/index.html) which allows remote and local management access to the system. Managing the various parts of Oracle Solaris is done through corresponding RAD modules. By layering the REST API on top of RAD anyone using this REST API can directly use all of the functionality in these RAD modules.

In the featured Jupyter notebooks we're making use of the Python `requests` module to talk to the REST API in Oracle Solaris. Where the intent is to show how using the `requests` module you can access the various parts of the RAD module and how to use them.

One of the benefits of using Python and Jupyter notebooks is that the behavior of the REST API and the RAD modules can be easily translated to other tools using REST to talk to the Oracle Solaris instance. 

Note that every Oracle Solaris Zone and Logical Domain has its own RAD/REST interface which can be independently turned on and accessed. 

[How to turn remote connection on](Settinguptheconnection.md)

[How to install Jupyter](https://jupyter.org/install)

## Using the Solaris Compliance REST API Notebook

The Solaris Compliance Framework allows you to assess the current state of the Solaris instance against a certain assessment profile. This assessment profile is a set of tests defined in a Compliance Benchmark. Oracle Solaris ships with two security benchmarks: Solaris (the recommended security configuration), and PCI-DSS (the benchmark for the Payment Card Industry). Each of these benchmarks ships with their own profiles. Optionally you can tailor your profile to the needs on the specific system you're going to assess. For more information on the Solaris Compliance Framework please refer to the [Oracle® Solaris 11.4 Compliance Guide](https://docs.oracle.com/cd/E37838_01/html/E61020/index.html).

![Compliance_REST_API_Jupyter](Compliance_REST_API_Jupyter.png)

The Compliance RAD/REST module allows you to connect to the Compliance Framework and do the following things:

- List Reports
  - Get basic data on reports
  - Download full reports
- Run new compliance assessments
  - Controlling name, benchmark, and profile that is used in the new assessment
- Delete reports
- Get info on benchmarks, profiles, and tailorings
  - List available benchmarks, and their profiles and tailorings
  - Get info on individual benchmark rules and what they test 

This Jupyter notebook will show how to do all of these steps.
