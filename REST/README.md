# Managing Oracle Solaris through REST

Oracle Solaris has a built-in framework to remotely manage its features called the [Remote Administration Daemon (RAD)](https://docs.oracle.com/cd/E37838_01/html/E68270/gmfhf.html#scrolltoc). This is done through [RAD modules](https://docs.oracle.com/cd/E37838_01/html/E68270/gsdwb.html) for each feature. Oracle Solaris 11.4 offers a REST API that is layered on top of the RAD framework, referred to as the RAD/REST API, or just the REST API.

You can use this RAD/REST API to connect to the Oracle Solaris system with any tool that can speak REST, giving a lot of freedom to connect in your favourite monitoring or management tool.

In this repository we're showing two examples of this. One is [Postman](https://www.postman.com), a development tool that allows for REST API development and testing, we've included a set of example REST calls that can be loaded into Postman and used to connect to and try out the Oracle Solaris REST API.

The other is [Jupyter](https://jupyter.org), this is a web-based interactive development environment that allows you to create *notebooks*. These are a web document that has a language kernel running behind it, and allows the text in the document to be executed live in this kernel. In our case we're using them to run Python code that shows how to connect to and use the Oracle Solaris REST API.

Here is where you can start working with:

- [Postman](/REST/Postman)
- [Jupyter Notebooks](/REST/python/notebooks)

## Enabling the REST API

In order to remotely connect to the Oracle Solaris instance over the RAD/REST interface you'll need to enable the *RAD Remote Service*. This SMF service,  also known as `rad:remote`, will both [turn on the capability](https://docs.oracle.com/cd/E88353_01/html/E72487/rad-8.html#REFMAN8rad-8) to talk to RAD remotely as well as turn on the REST API, by default on port `6788`. By default this service will be turned off. This is in conformance with our secure by default policy that only enables the bare minimum in remotely accessible strongly authenticated services. In the future we might choose to add the RAD remote service to this bare minimum list. Once the service is on it'll stay on until to turn it off.

Note that in Oracle Solaris 11.3 you could also connect over REST but [you needed to configure a custom SMF service](https://docs.oracle.com/cd/E53394_01/html/E54825/gpztv.html#scrolltoc) before you could enable it. With the release of Oracle Solaris 11.4 there is the prebuilt `rad:remote` SMF service that you only need to enable. In the Oracle Solaris 11.3 case you will need to also choose your own service parameters, like port number.

For a more in-depth description see the [How-to article on setting up the connection](setting_up_the_connection.md).

## Using Certificates

To be able to connect over RAD/REST we require you use the secure *https* transport and in order for this to the system you're connecting to must have a valid SSL certificate in place for the client to know it can be trusted. 

Many production systems will have certificate in place issued by either a *public CA* (Certificate Authority) or an *internal CA* managed by the company (we're calling these a *managed CA*). However quite often systems you're testing on might not have one of these certificates from a managed CA. For example you might be using a Oracle Solaris running in VirtualBox on your laptop. In this case to still be able to connect to the server you'll need to copy the self-signed certificate the host CA created over to the system you're connecting from.

By default in Oracle Solaris 11.4 the `identity:cert` service will act as the host CA and create the certificates using the hostname and DNS name information it can find after installation. It will create and put them in `/etc/certs/localhost/hoast-ca/` and it's the `hostca.crt` you're looking to copy across (the `hostca.key` should remain in place). It's important to realize that the name or IP address that the certificate was created with should be the same as the name or IP address that the client sees, if it doesn't match you'll have to create a certificate by hand and then put it in the same location.

Once you have the certificates created, copied and the SMF service started you can use your favorite client tool and start connecting with the server.

If you're going to be connecting to multiple servers with self-signed certificates, you will probably want to rename the `hostca.crt` you've copied from each server to know which file goes with which server.

## More Documentation

So now you know how to connect, the next question that tends to rise is where to find an explanation of the full RAD/REST API. There are of course the online [docs on the RAD interface](https://docs.oracle.com/cd/E37838_01/html/E68270/index.html) which also has a [section on REST in it](https://docs.oracle.com/cd/E37838_01/html/E68270/gpzxz.html#scrolltoc). But this is by no means a complete description of the API. Plus the API is also dynamic, as we add RAD modules there are more endpoints to talk to. To solve for this we've included a documentation package in Oracle Solaris 11.4 called `webui-docs`, that when added to the system with give an extra *Application* in the Oracle Solaris WebUI. Once installed you'll see "**Solaris Documentation**" as an option below "**Solaris Analytics**" and "**Solaris Dashboard**" in the "**Applications**" pull-down menu. Once selected you'll see a link to "**Solaris APIs**", and clicking this will bring you to the full REST API description of all the RAD modules on that system.



Copyright (c) 2022, Oracle and/or its affiliates.
 Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.