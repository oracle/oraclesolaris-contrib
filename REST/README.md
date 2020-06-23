# Managing Oracle Solaris through REST

To be able to connect over RAD/REST we require you use the secure *https* transport and in order for this to work your server — i.e. the system you're connecting to — must have a valid SSL certificate in place for the client to know it can be trusted. Many production systems will have certificate in place issued by either a *public CA* (Certificate Authority) or an *internal CA* managed by the company (I'll call these a *managed CA*). However quite often systems you're testing on might not have one of these certificates from a managed CA. For example you might be using a Oracle Solaris running in VirtualBox on your laptop. In this case to still be able to connect to the server you'll need to copy a certificate the host CA created over to the system you're connecting from.

By default in Oracle Solaris 11.4 the `identity:cert` service will act as the host CA and create the certificates using the hostname and DNS name information it can find after installation. It will create and put them in `/etc/certs/localhost/` and it's the `host.crt` you're looking to copy across (the `host.key` should remain in place). It's important to realize that the names that the certificate was created with should be the same as the name the client sees, if it doesn't match you'll have to create a certificate by hand and then put it in the same location.

The other thing you'll need to do is enable the *RAD Remote* service. This is an SMF service that allows you to connect remotely to the system over REST. By default this service will be turned off. This is in conformance with our secure by default policy that only enables the bare minimum in remotely accessible strongly authenticated services. In the future we might choose to add the RAD remote service to this bare minimum list. Once the service is on it'll stay on until to turn it off.

Note that in Oracle Solaris 11.3 you needed to configure a custom SMF service before you could enable it. With the release of Oracle Solaris 11.4 there is a prebuilt SMF service — called `rad:remote` — that you only need to enable. In the Oracle Solaris 11.3 case you choose your own service parameters, like port number.

Also note that if you've created your own certificate you'll need to make sure that either the custom certificate is placed in the location the `rad:remote` service is expecting it or you change the service configuration to point to your certificates.

Once you have the certificates created, copied and the SMF service started you can use your favorite client tool — Curl, Python, Postman — and start connecting with the server.

## Setting Up the RAD/REST Service

This blog will assume you're using Oracle Solaris 11.4, if you're using Oracle Solaris 11.3 you'll need to create/configure your the `rad:remote` service first, for more details [read the RAD Developer's Guide](https://docs.oracle.com/cd/E53394_01/html/E54825/gpztv.html#scrolltoc).

### Enabling `rad:remote`

On the server enable the `rad:remote` service and check it's running:

```shell
root@test_server:~# svcadm enable rad:remote
root@test_server:~# svcs -l rad:remote
fmri         svc:/system/rad:remote
name         Remote Administration Daemon
enabled      true
state        online
next_state   none
state_time   Mon Jun 24 22:22:37 2019
logfile      /var/svc/log/system-rad:remote.log
restarter    svc:/system/svc/restarter:default
contract_id  918 
manifest     /lib/svc/manifest/system/rad.xml
dependency   require_all/refresh svc:/system/identity:cert (online)
dependency   require_all/none svc:/milestone/multi-user (online)
dependency   require_all/none svc:/system/filesystem/minimal:default (online)
```

Now it's running, you can connect to the system remotely.

### Copying The Certs

In case where you're system is using a certificate issued by the host CA — like in my case — you'll need to copy that across to your client system first:

```shell
-bash-4.4$ scp testuser@test_server.example.com:/etc/certs/localhost/host.crt .
Password: 
host.crt                                                           100% 1147   666.9KB/s   00:00   
```

Now we can use the `host.crt` in all our REST conversations that connect to this server.

## Testing the Connection

Before we'll connect to the server, I need to make a short detour to talk about the two authentication methods Oracle Solaris supports. The first one was introduced in Oracle Solaris 11.3 and uses a single step with a JSON datafile that contains both username and password. It looks something like this:

```json
{
  "username": "testuser",
  "password": "your_password",
  "scheme": "pam",
  "preserve": true,
  "timeout": -1
}
```

And this authentication method can be found at `/api/authentication/1.0/Session/`.

The second method was introduced in Oracle Solaris 11.4 and is a two step process where you first send the username, and once this is met with success, you send the password. The two JSON data files would something like this:

```json
{
  "username":"testuser", 
  "preserve": true
}
```

and:

```json
{
  "value": {
      "pam": {"responses": ["your_password"]}, 
      "generation": 1
  }
}
```

This second authentication method can be found at `/api/authentication/2.0/Session/`.

This second method was added to allow for more advanced authentication methods like two-factor authentication for javascript based apps like the Oracle Solaris WebUI. For our purposes the first one works fine. I've put the JSON data in a file called `login.json` and will refer to it in the coming examples.

### Using Curl

On the client, from the directory I put the certificate in I can run:

```shell
-bash-4.4$ curl -c cookie.txt -X POST --cacert host.crt --header 'Content-Type:application/json' --data '@login.json' https://test_server.example.com:6788/api/authentication/1.0/Session/
{
        "status": "success",
        "payload": {
                "href": "/api/com.oracle.solaris.rad.authentication/1.0/Session/_rad_reference/2560"
        }
}
```

Note, I'm using a `cookie.txt` file to save the session cookies. And the response shows success and an `href` if I need it.

I can now for example ask the SMF RAD module to list the RAD services it has:

```shell
-bash-4.4$ curl -b cookie.txt --cacert host.crt -H 'Content-Type:application/json' -X GET https://test_server.example.com:6788/api/com.oracle.solaris.rad.smf/1.0/Service/system%2Frad/instances
{
        "status": "success",
        "payload": [
                "local",
                "remote"
        ]
}
```

Note again that I'm referring to the `cookie.txt` file to use the current session's cookie. And you see it knows of a local and a remote service.

Now to check the current status of the `rad:remote` service:

```shell
-bash-4.4$ curl -b cookie.txt --cacert host.crt -H 'Content-Type:application/json' -X GET https://test_server.example.com:6788/api/com.oracle.solaris.rad.smf/1.0/Instance/system%2Frad,remote/state
{
        "status": "success",
        "payload": "ONLINE"
}
```

And the service is online, not a surprise I guess.

### Using Python

To illustrate how to the same using Python I have a short example script. Note this is a very basic script with hardly any error handling and pretty ugly code, the point is to illustrate the way to connect. Here's my code:

```python
import requests                                                                 
import json                                                                     

config_filename = "login.json"

try:
    with open(config_filename, 'r') as f:
        config_json = json.load(f)
except Exception as e:
    print(e)

#Build session
with requests.Session() as s:

    #Login to server
    login_url = "https://test_server.example.com:6788/api/authentication/1.0/Session"
    print("logging in to the Server")
    r = s.post(login_url, json=config_json, verify='host.crt')
    print("The status code is: " + str(r.status_code))
    print("The return text is: " + r.text)

    # Get list of all SMF instances of the RAD module
    query_url0 = "https://test_server.example.com:6788/api/com.oracle.solaris.rad.smf/1.0/Service/system%2Frad/instances"
    print("Getting the list of SMF instances of the RAD module")
    r = s.get(query_url0)

    print("The status code is: " + str(r.status_code))
    print("The return text is: " + r.text)

    # Getting the status of the rad:remote module
    query_url1 = "https://test_server.example.com:6788/api/com.oracle.solaris.rad.smf/1.0/Instance/system%2Frad,remote/state"
    print("Getting the status of the rad:remote module")
    r = s.get(query_url1)
    print("The status code is: " + str(r.status_code))
    print("The return text is: " + r.text)
```

And this is what it returns:

```shell
-bash-4.4$ python sample.py
logging in to the Server
The status code is: 201
The return text is: {
        "status": "success",
        "payload": {
                "href": "/api/com.oracle.solaris.rad.authentication/1.0/Session/_rad_reference/3840"
        }
}
Getting the list of SMF instances of the RAD module
The status code is: 200
The return text is: {
        "status": "success",
        "payload": [
                "local",
                "remote"
        ]
}
Getting the status of the rad:remote module
The status code is: 200
The return text is: {
        "status": "success",
        "payload": "ONLINE"
}
```

You see the same result.

## More Documentation

So now you know how to connect, the next question that tends to rise is where to find an explanation of the full RAD/REST API. There are of course the online [docs on the RAD interface](https://docs.oracle.com/cd/E37838_01/html/E68270/index.html) which also has a [section on REST in it](https://docs.oracle.com/cd/E37838_01/html/E68270/gpzxz.html#scrolltoc). But this is by no means a complete description of the API. Plus the API is also dynamic, as we add RAD modules there are more endpoints to talk to. To solve for this we've included a documentation package in Oracle Solaris 11.4 called `webui-docs`, that when added to the system with give an extra *Application* in the Oracle Solaris WebUI. Once installed you'll see "**Solaris Documentation**" as an option below "**Solaris Analytics**" and "**Solaris Dashboard**" in the "**Applications**" pull-down menu. Once selected you'll see a link to "**Solaris APIs**", and clicking this will bring you to the full REST API description of all the RAD modules on that system.