# Managing Oracle Solaris through REST

To be able to connect over RAD/REST we require you use the secure *https* transport and in order for this to work your server — i.e. the system you're connecting to — must have a valid SSL certificate in place for the client to know it can be trusted. Many production systems will have certificate in place issued by either a *public CA* (Certificate Authority) or an *internal CA* managed by the company (I'll call these a *managed CA*). However quite often systems you're testing on might not have one of these certificates from a managed CA. For example you might be using a Oracle Solaris running in VirtualBox on your laptop. In this case to still be able to connect to the server you'll need to copy a certificate the host CA created over to the system you're connecting from.

By default in Oracle Solaris 11.4 the `identity:cert` service will act as the host CA and create the certificates using the hostname and DNS name information it can find after installation. It will create and put them in `/etc/certs/localhost/` and it's the `host.crt` you're looking to copy across (the `host.key` should remain in place). It's important to realize that the names that the certificate was created with should be the same as the name the client sees, if it doesn't match you'll have to create a certificate by hand and then put it in the same location.

The other thing you'll need to do is enable the *RAD Remote* service. This is an SMF service that allows you to connect remotely to the system over REST. By default this service will be turned off. This is in conformance with our secure by default policy that only enables the bare minimum in remotely accessible strongly authenticated services. In the future we might choose to add the RAD remote service to this bare minimum list. Once the service is on it'll stay on until to turn it off.

Note that in Oracle Solaris 11.3 you needed to configure a custom SMF service before you could enable it. With the release of Oracle Solaris 11.4 there is a prebuilt SMF service — called `rad:remote` — that you only need to enable. In the Oracle Solaris 11.3 case you choose your own service parameters, like port number.

Also note that if you've created your own certificate you'll need to make sure that either the custom certificate is placed in the location the `rad:remote` service is expecting it or you change the service configuration to point to your certificates.

Once you have the certificates created, copied and the SMF service started you can use your favorite client tool — Curl, Python, Postman — and start connecting with the server.

Here is where you can start working with Jupyter Notebooks:

- [Jupyter Notebooks](/python/notebooks)
- [Postman](/Postman)

## More Documentation

So now you know how to connect, the next question that tends to rise is where to find an explanation of the full RAD/REST API. There are of course the online [docs on the RAD interface](https://docs.oracle.com/cd/E37838_01/html/E68270/index.html) which also has a [section on REST in it](https://docs.oracle.com/cd/E37838_01/html/E68270/gpzxz.html#scrolltoc). But this is by no means a complete description of the API. Plus the API is also dynamic, as we add RAD modules there are more endpoints to talk to. To solve for this we've included a documentation package in Oracle Solaris 11.4 called `webui-docs`, that when added to the system with give an extra *Application* in the Oracle Solaris WebUI. Once installed you'll see "**Solaris Documentation**" as an option below "**Solaris Analytics**" and "**Solaris Dashboard**" in the "**Applications**" pull-down menu. Once selected you'll see a link to "**Solaris APIs**", and clicking this will bring you to the full REST API description of all the RAD modules on that system.







Copyright (c) 2020, Oracle and/or its affiliates.
 Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.