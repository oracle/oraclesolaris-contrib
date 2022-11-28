## Setting Up the RAD/REST Service

The README file assumes you're using Oracle Solaris 11.4, if you're using Oracle Solaris 11.3 you'll need to create/configure your the `rad:remote` service first, for more details [read the RAD Developer's Guide](https://docs.oracle.com/cd/E53394_01/html/E54825/gpztv.html#scrolltoc).

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

In case where you're system is using a self-signed certificate issued by the host CA — like in my case — you'll need to copy that across to your client system first:

```bash
-bash-4.4$ scp testuser@test_server.example.com:/etc/certs/localhost/host-ca/hostca.crt .
Password: 
hostca.crt                                                           100% 1147   666.9KB/s   00:00   
```

Now we can use the `hostca.crt` in all our REST conversations to validate the server in the connections.

A tip, when you copy the self-signed certificate over from the server it is helpful to rename the file to reflect which server it belongs to, especially if you're going to be connecting to multiple servers with self-signed certificates.

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

The second additional method was introduced in Oracle Solaris 11.4 and is a two step process where you first send the username, and once this is met with success, you send the password. The two JSON data files would something like this:

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

This second method was added to allow for more advanced authentication methods like two-factor authentication for javascript based apps like the Oracle Solaris WebUI. For our purposes the first one works fine. I've put the JSON data in a file called `login.json` and will refer to it in the coming examples. Both will work on Oracle Solaris 11.4.

Oracle Solaris 11.4 SRU33 introduced a third option, using an X.509 Client Certificate. This avoids the need for using a username/password combination—and the risks of exposing them, and instead uses a pre-signed certificate that the connecting application can use to authenticate. An added advantage of this method is that you can use it directly on the REST call you want to use for your control or data request, instead of having to do an authentication call first and then to the control or data call with a second call. For more informaiton on how to use it see [Using the X.509 Client](Using_the_X509_Client.md) doc.

### Using Curl

As an example of using the first authentication method, on the client—from the directory that holds the `hostca.crt` and `login.json` files—I can run:

```shell
-bash-4.4$ curl -c cookie.txt -X POST --cacert hostca.crt --header 'Content-Type:application/json' --data '@login.json' https://test_server.example.com:6788/api/authentication/1.0/Session/
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
-bash-4.4$ curl -b cookie.txt --cacert hostca.crt -H 'Content-Type:application/json' -X GET https://test_server.example.com:6788/api/com.oracle.solaris.rad.smf/1.0/Service/system%2Frad/instances
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

There's much more information on how to do this in the [Jupyter notebooks section](python/notebooks), but to illustrate how to the do the same using Python, here's a short example script. Note this is a very basic script with hardly any error handling and pretty ugly code, the point is to illustrate the way to connect:

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
    r = s.post(login_url, json=config_json, verify='hostca.crt')
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

Copyright (c) 2022, Oracle and/or its affiliates. Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.