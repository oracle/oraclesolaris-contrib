## Automating Migration from Oracle VirtualBox to Oracle Cloud Infrastructure

Many modern software development toolchains include testing an entire virtual machine in a cloud environment. This may require automation which migrates a VM from a developer's computer to a cloud. This article describes automation that can be uesd to migrate a copy of a VM into Oracle Cloud Infrastructure, starting with a Oracle Solaris 11.4 VM installed in Oracle VirtualBox.

This article assumes you have installed and configured the OCI CLI software on your local computer - the same one that's running VirtualBox. The steps to do this depend on your operating system, but [instructions are available](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm). It also assumes that you have some basic experience with the OCI console, and assumes you have [installed a Solaris VM in your VirtualBox environment](https://www.oracle.com/it-infrastructure/technologies/handsonlab-solaris11-on-vm-virtualbox.html).

This is a follow-on to [an article that describes how to use the VirtualBox and OCI Consoles to migrate an Oracle Solaris 11.4 VBox VM to OCI](https://blogs.oracle.com/solaris/post/migrating-oracle-solaris-to-oci-using-virtualbox-7). However, this article shows how to automate the process so that you can perform it repeatedly with little effort.

At a high level, the steps to perform include:

1. Create a new [OCI Object Storage bucket](https://docs.oracle.com/en-us/iaas/Content/Object/Concepts/objectstorageoverview.htm#Overview_of_Object_Storage) ("bucket") in which you will temporarily store an image of the VirtualBox VM. (This is needed unless have an existing bucket.)
2. Export an image of the VirtualBox VM in [OVA](https://en.wikipedia.org/wiki/Open_Virtualization_Format) format as a local file.
3. Copy the OVA file to OCI, as a new object in the OCI bucket.
4. Import the object from the bucket into an [OCI custom image](https://docs.oracle.com/en-us/iaas/Content/Marketplace/Concepts/marketoverview.htm).
5. Launch an [OCI compute instance](https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm) from the custom image.

Fortunately, there isn't much work for you to do: there is one command to perform each of those steps. Also, all of the commands execute on your local computer, so the automation can all exist in one file.

This example is limited to a depiction of only the features needed to create an OCI instance that replicates a VirtualBox guest in OCI. Because of this, we offer some cautions. First, the OCI instance created using the commands shown below may have a public IP address. You should not use a public IP address on an OCI instance unless it requires access to the Internet, and then only after a thorough security analysis. Second, these commands use default values for many OCI objects. When you are ready to move past the basic demonstration shown here, you should learn about these OCI concepts and how to create, configure and specify them:

- [Regions and Availibility Domains](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm)
- [Virtual Cloud Networks](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm)
- [Tenancy and Compartments](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm) (parts of IAM)
- [Security Components](https://docs.oracle.com/en-us/iaas/Content/Security/Concepts/security_guide.htm)
- [Routing and Gateways](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm#Private)

For this article, the automation is written in Unix/Linux bash language. You may need to modify it for a different language.

These shell variables enhance readability of the commands below. You must modify them to fit your needs.

```
OCI_REGION=us-phoenix-1    # Name of the OCI region you use - modify as necessary.
OCI_NS=MYNAMESPACE         # Your OCI Namespace
BUCKET_NAME=vbox-upload    # Your name for the OCI bucket that will temporarily hold the .ova file.
OVA_NAME=solaris11oci.ova  # Name of the local .ova file to create when you export the VirtualBox VM.
VM_NAME=solaris11oci       # The name of the VirtualBox guest VM that is the source of the OCI image.
AD_NAME=ruWb:PHX-AD-1      # Availability Domain where you want the OCI instance to run.
IMAGE_NAME=solaris11oci    # Your name for the Solaris 11 image in OCI.
OCI_SHAPE=VM.Standard2.1   # OCI Shape for the instance to be created - choose the shape you want.

# Your OCI Compartment's OCID
COMP_OCID=ocid1.compartment.oc1..aaaaaaaaaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# The subnet for the instance to be created.
SUBNET_OCID=ocid1.subnet.oc1.phx.aaaaaaaaaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

This variable is a URI used on your local computer to indicate the location of the OVA file that VirtualBox creates.

```
# The URI of the object in the bucket that stores the VM's .ova file before creating an OCI image.
BUCKET_OBJ_URI=https://objectstorage.$OCI_REGION.oraclecloud.com/n/$OCI_NS/b/$BUCKET_NAME/o/$OVA_NAME
```

One command exports a copy of the VirtualBox guest to local storage:

```
VBoxManage export $VM_NAME -o $OVA_NAME
```

Two commands create a new OCI bucket, and copy the OVA file created in the previous command into the bucket as a new object. You can use an existing OCI bucket if you prefer, in which case you would omit the first command.

```
oci os bucket create -c $COMP_OCID --name $BUCKET_NAME | grep ocid1.bucket | cut -d: -f 2 | tr -d \",
oci os object put -ns $OCI_NS -bn $BUCKET_NAME --name $OVA_NAME --file $OVA_NAME
```

One command imports the OVA file from the bucket into a new OCI custom image, and assigns it a human-friendly name:

```
oci  compute image import from-object-uri --uri $BUCKET_OBJ_URI -c $COMP_OCID  --display-name $IMAGE_NAME
```

Finally, one command launches an OCI compute instance from the new custom image:

```
oci compute instance launch \
    --availability-domain $AD_NAME \
    --compartment-id $COMP_OCID \
    --image-id $IMAGE_OCID  \
    --shape $OCI_SHAPE      \
    --ssh-authorized-keys-file  ~/.ssh/oci_key_public.pem  \  
    --subnet-id $SUBNET_OCID
```

The instance will be available in a few minutes.

The entire script including those commands can be found at [our github repo](https://github.com/oracle/oraclesolaris-contrib/tree/master/OracleSolaris_OCI/07_Automating_Migration_From_Oracle_VirtualBox_to_OracleCloudInfrastructure), along with additional commands that improve usability.



Copyright (c) 2020, 2023 Oracle and/or its affiliates.

Released under the Universal Permissive License v1.0 as shown at

[https://oss.oracle.com/licenses/upl/](https://oss.oracle.com/licenses/upl/)