# OCI Python API — Basic

As part of of our [series of blogs on how to launch an Oracle Solaris instance on OCI](https://blogs.oracle.com/solaris/post/oracle-solaris-shines-through-the-cloud) this blog explains how to use the OCI Python API to complete this task. First we'll explain the main flow of steps you take to launch the instance, then we'll shortly discuss the main API endpoints we're using, then where to find the Jupyter notebooks with the example code in them, and finally we'll go through all the steps.

Note that many of the steps we're using are leveraging information and code supplied by the Oracle Linux team in their [`oci-compute` script](https://github.com/oracle/oracle-linux/tree/main/oci-compute) hosted on their GitHub page, and the [blog](https://blogs.oracle.com/linux/post/easy-provisioning-of-cloud-instances-on-oracle-cloud-infrastructure-with-the-oci-cli) that [Philippe van Haesendonck](https://blogs.oracle.com/authors/philippe-vanhaesendonck) wrote about it, it's quite excellent. Their script takes much more into account than we do, like the ability to use platform images and custom images. Where we're currently only focused on the steps needed for a Marketplace image. So if you want a pre-written script to do these things I'd advise you use their script, this blog is for folks who want to understand the underlying steps and maybe write their own script.

For more information about OCI terminology and Marketplace components please refer to our [earlier blog](https://blogs.oracle.com/solaris/post/oracle-solaris-on-oci-marketplace-components) on this.

## General flow to launch an instance

Here's the high-level flow on how to launch the Oracle Solaris instance:

- Connect to the Marketplace and find the Oracle Solaris image that you want to use
- Check if you've already agreed to the license for this image, and if not, agree to the license
- Collect all the information needed to launch the instance in a Python object
- Launch the instance using this information

## Using the Jupyter notebooks

We've found that supplying [Jupyter notebooks](https://jupyter.org/) with a full example is a very useful tool to better help explain how to do things in Python, especially if there's a specific sequence of steps that you need to follow. In this light we're also supplying two Jupyter notebooks on our [`oraclesolaris-contrib` GitHub page](https://github.com/oracle/oraclesolaris-contrib), one that achieves launching the instance in the fewest amount of Python steps, and the second that has more complexity that automates more for you. One of the main differences is in how much Information you supply upfront in the config files about the Availability Domain, VCN, and Subnet you'd like to use or if Python goes and fetches this for you. 

The advantage of this is that when using a Jupyter notebook yourself, you can edit the config files and run through the actual steps using your own OCI access. You can also alter the Python code in case you want to try something else. This way you can follow along with the steps and better learn what they do.

The basic notebook can be found [here](oci-python-basic.ipynb), and the more advanced one [here](oci-python-full.ipynb). This blog will focus on explaining the steps in the basic version.

## Using the Python API endpoints

OCI has many API endpoints for Python, for this task we're only going to use a few of them. In this case we're actually going to use a few classes where the instances work as clients, that you give your account information, and you can use over and over to connect to OCI. Here are the four clients we're going to use:

- `oci.marketplace.MarketplaceClient()` — We'll need to use this client to find the latest Oracle Solaris marketplace image
- `oci.core.ComputeClient()` — We'll need to use this client to do the main starting and stopping of the compute instances
- `oci.identity.IdentityClient()` — We'll need to use this client to locate the official name of your Availability Domain
- `oci.core.VirtualNetworkClient()` — We'll need to use this client to find the official names of your VCNs and the Subnet you're using

We will also need to create and use two files that hold our configuration information. One is the regular `config` file that is also used by the OCI CLI, and holds information like your user, tenancy, and region info. We use this to initialize the clients mentioned above. The other is a file you'll have to create yourself that holds information on things specific to the instance you'd like to launch like the shape, compartment, and others things you'd normally interactively choose when using the Oracle Cloud Console to launch an instance. In our notebook we've called it `oci_compute_rc`. We load both these files at the beginning of the notebook to have all the configuration data needed to launch the instance.

For more information about the Python APIs used please refer to the documentation on the [Marketplace](https://docs.oracle.com/en-us/iaas/tools/python/2.88.1/api/marketplace.htmlhttps://docs.oracle.com/en-us/iaas/tools/python/2.89.0/api/marketplace.html) and [Core Compute](https://docs.oracle.com/en-us/iaas/tools/python/2.89.0/api/core.html) APIs.

## Explaining the steps

Now to explain the steps. Note that we're assuming you can read along in the Jupyter notebook with this example. And like the other blogs, we're also assuming you have all the things set up that you will need to launch a new instance, like a Compartment, VCN, and Subnet.

### Information you need first

After loading the required libraries and variables, we need to load the `config` and `oci_compute_rc` files to load in you preferences. If you have not already created them this is the moment to do so before you load them into Python. 

This step also initializes the four OCI client objects we need to talk to OCI.

### Find the Oracle Solaris Marketplace image you want to use 

To find the Oracle Solaris 11.4 Marketplace image you first need to find its listing. This is done by using the Marketplace client's `list_listings()` function and searching for "Oracle Solaris 11.4" in the listing name.

The Oracle Solaris listing has multiple versions of Oracle Solaris 11.4 that you can choose from, these versions are in what the OCI Marketplace calls packages, so using the ID for the listing from above, you can use the `list_packages()` function to list the associated packages and by sorting them in age you can easily find the latest version of Oracle Solaris 11.4. You can then use this information to fetch all the data associated with this package so you can now go to the next step. 

### Check the license status of the Marketplace image

Now you have the data of the package we're looking for you need to check if you've already agreed to the license for this version of Oracle Solaris in this compartment. To do this you use `list_agreements()` to search for the *agreements* against this package, and you search for the *accepted agreements* with `list_accepted_agreements()`. Using these two sets you can check if there is a match. If so you're good, if not you'll have to accept the agreement.

Note that an "agreement" isn't the same as an "accepted agreement", but rather the "agreement" has information in it that can be used to create an "accepted agreement", and only with an "accepted agreement" in place can you launch an instance using this image.

#### (If needed) Accept the agreement

In the case that there is no accepted agreement in place, you need to get the agreement and use the `CreateAcceptedAgreementDetails()` function to create an object with all the data in it needed to accept the agreement and then run the `create_accepted_agreement()` function with this data and you should be ready to proceed.

### Prep the image definition object

To create the instance we need to define a set of Python variables and objects:

- Display Name — This is the name you want to give the instance
- Compartment ID — The compartment the instance should run in
- Availability Domain Name — The Availability Domain the instance should run in
- Shape Name — The Shape this instance should use
- VNIC Details Object — An object that holds all the data on the network the instance should be connected to
- Image Details Object — An object created using the Marketplace image data that holds all the information needed about the image
- Metadata Object — An object that holds information like where the SSH key is located you'd like to upload into the instance

The steps in this section use information provided in the config files and the Marketplace image data to eventually create an object that is passed into the launch function to correctly define and launch the instance. This final step is done with the `LaunchInstanceDetails()` function and once you have this you're all set.

### Launch the Oracle Solaris instance

Now that you're ready to launch the instance, there's a bit of magic that has to be done to deal with the fact that the actual launching of the instance may take a while. So you can actually tell OCI to launch the instance and wait for a specific state in the instance lifecycle to happen before it returns. This is done with the `launch_instance_and_wait_for_state()` function, which is passed the *launch instance details* object from above and an argument called `wait_for_states` which is a list of one or more states you want to wait for. In this case we'll be waiting for the `oci.core.models.Instance.LIFECYCLE_STATE_RUNNING` state. So once the instance has transitioned into this state we're ready.

The reason the launch can take a while is because OCI needs to copy the image into place, ready the infrastructure, and then provision and start the instance. And as with all OS instances this takes a bit of time. Note that as you may know, on the first start Oracle Solaris will also go through a set of initializations, mostly in SMF, so even though OCI may say the instance is running you may need wait a bit before you can connect to it over SSH.

Finally, we've added a few commands to get some extra information about your running instance, for example the public and private IP addresses it was given so you can SSH into it.

## In summary

Using the Python API for OCI is a very powerful and versatile way of interacting with OCI and it gives you a good way to automate the creation of Oracle Solaris instances into your infrastructure. Using the Jupyter notebook should allow you to test run and experiment with the API on your own, do by all means, go to our [`oraclesolaris-contrib` GitHub page](https://github.com/oracle/oraclesolaris-contrib), pull in the Jupyter notebook and try it!

Copyright (c) 2022, Oracle and/or its affiliates. Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/. 