# Example REST Calls for Postman

The JSON file contains example REST calls that can be used with the [Postman tool](https://www.postman.com). To use the file you'll need to import it as a *Collection* into Postman. Once imported you'll also need to edit the server, username, and password files to fit your system. You may also need to import the server hostca.crt certificate file if you want to securely connect to the server and it doesn't have a registered certificate.

## Importing the Collection

To import the JSON file through either the **Import...** option in the **Edit** menu or by clicking the **Import** button in the top left corner of the tool:

![Import_Button](/StatsStore_WebUI/Images/Postman/Postman_image_01.png)

Then after expanding the new *Collection* in the left bar it should look something like this:

![Import_Result](/StatsStore_WebUI/Images/Postman/Postman_image_02.png)

Each folder in the collection holds one or more REST calls.

## Editing the Collection Variables

Then look for the **...** next to the Collection name, on its righthand side and select **Edit**:

![Import_Button](/StatsStore_WebUI/Images/Postman/Postman_image_03.png)

This opens the **EDIT COLLECTION** window, then select the **Variables** tab and replace the placeholder values with your own:

![Import_Button](/StatsStore_WebUI/Images/Postman/Postman_image_04.png)

Then click **Update**.

> **Note:** There's an entry for both **server** and **global-zone** as you want to connect to a zone (in our case named **server**) and it's Global Zone.

## Starting a Session 

When you expand the **Authentication** folder, you'll see different authentication options, the first two are using the v1.0 of the Authentication API — One for the regular commands and one for commands specific to a Global Zone — the second two are for the v2.0 of the Authentication API:

![Import_Button](/StatsStore_WebUI/Images/Postman/Postman_image_05.png)

The difference between v1.0 and v2.0 is that v1.0 puts the *username* and *password* in one **POST** request, where v2.0 uses a **POST** request for sending the *username* and a separate **PUT** request for the *password*. You can use either, the first is simpler to use, the second allows for techniques like 2 factor authentication.

## Using the _rad_reference

In many cases you'll get a response list this:

```
{
        "status": "success",
        "payload": {
                "href": "/api/com.oracle.solaris.rad.authentication/1.0/Session/_rad_reference/1536"
        }
}
```

Where it returns a `_rad_reference` and in most cases you don't need to do anything with this but in cases when you want to follow the first call up with a second one you'll need to use the reference number added to this second call. 

For example in the v2.0 Authentication API, the username **POST** returns:

```
"href": "/api/com.oracle.solaris.rad.authentication/2.0/Session/_rad_reference/2304"
```

And the **PUT** call then needs to look like this:

```
https://{{server}}:6788/api/com.oracle.solaris.rad.authentication/2.0/Session/_rad_reference/2304/state
```

Where the reference `2304` is copied across.

Another example the *Get the pkg fmri of  entire* call which searches for a package — in this collection `"entire"` — it returns:

```
{
        "status": "success",
        "payload": [
                {
                        "href": "/api/com.oracle.solaris.rad.ips/1.0/PkgFmri/_rad_reference/2050"
                }
        ]
}
```

This can then be used with the *Get IPS fmri details: fmri* call in it's URL:

```
https://{{server}}:6788/api/com.oracle.solaris.rad.ips/1.0/PkgFmri/_rad_reference/2050/_rad_method/get_fmri
```

Which in turn returns:

```
{
        "status": "success",
        "payload": "pkg://solaris/entire@11.4,5.11-11.4.24.0.1.75.2:20200729T195424Z"
}
```

So look carefully what the URL looks like and if you need to replace the `_rad_reference` number.

Copyright (c) 2020, Oracle and/or its affiliates. Licensed under the Universal Permissive License v 1.0 as shown at <https://oss.oracle.com/licenses/upl/>.