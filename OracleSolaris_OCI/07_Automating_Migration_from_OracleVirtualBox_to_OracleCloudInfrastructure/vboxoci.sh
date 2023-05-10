### This script copies an Oracle VirtualBox VM to OCI.
#   It is meant for educational purposes, not for use as is.
#
# The original VirtualBox VM is not modified during this process.
#
# An OCI bucket is created as a temporary storage place. This bucket is not 
# emptied or destroyed by this script.
#
# Before using this script, you must install and configure the OCI CLI on
# the system running VirtualBox.
#
# You must also specify these shell variables:
# OCI_REGION : the name of the OCI region for this Solaris 11 instance
# OCI_NS : the name of your OCI namespace
# COMP_OCID : the OCID of your compartment
# SUBNET_OCID : the OCID of the subnet where the Oracle Solaris 11 should be attached.
# You can changed the other variables to any permitted values.

# Exit if anything fails so it doesn't try to perform a later step.
set -e

### Set these variables as appropriate for your situation
#
OCI_REGION=us-phoenix-1    # Name of the OCI region you use.
OCI_NS=MY_NAMESPACE        # Your OCI Namespace
BUCKET_NAME=vbox-upload    # Your name for the OCI bucket that will temporarily hold the .ova file.
OVA_NAME=solaris11oci.ova  # Name of the .ova file to create when you export the VirtualBox VM.
VM_NAME=solaris11oci       # The name of the VirtualBox guest VM that is the source of the OCI image.
AD_NAME=ruWb:PHX-AD-1      # Availability Domain where you want the OCI instance to run.
IMAGE_NAME=solaris11oci    # Your name for the Solaris 11 image in OCI.
OCI_SHAPE=VM.Standard2.1   # OCI Shape for the instance to be created.

# Your OCI Compartment's OCID
COMP_OCID=ocid1.compartment.oc1..aaaaa......c7w3q

# The subnet for the instance to be created.
SUBNET_OCID=ocid1.subnet.oc1.phx.aaaaa......y6tsa

# The URI of the object in the bucket that stores the VM's .ova file before creating an OCI image.
BUCKET_OBJ_URI=https://objectstorage.$OCI_REGION.oraclecloud.com/n/$OCI_NS/b/$BUCKET_NAME/o/$OVA_NAME

### Actual processing starts here!

# Export the Oracle Solaris 11 VM from VirtualBox
echo Creating an OVA image from the Oracle Solaris 11 VM in VirtualBox...
VBoxManage export $VM_NAME -o $OVA_NAME

echo Creating an OCI bucket in which to store the OVA image...
oci os bucket create -c $COMP_OCID --name $BUCKET_NAME | grep ocid1.bucket | cut -d: -f 2 | tr -d \",

echo Copying the OVA file to the bucket, as a new bucket object.
oci os object put -ns $OCI_NS -bn $BUCKET_NAME --name $OVA_NAME --file $OVA_NAME

echo Importing the OVA image from local storage into OCI...
IMAGE_OCID=`oci  compute image import from-object-uri --uri $BUCKET_OBJ_URI -c $COMP_OCID  --display-name $IMAGE_NAME | grep ocid1.image | cut -d: -f 2 | tr -d \",`

echo Waiting for the OCI image to be created from the bucket object...
while true; do
  state=`oci compute image get --image-id $IMAGE_OCID | grep lifecycle | cut -d: -f 2 | tr -d \",`
  echo At `date` the image is :$state:.
  if [[ $state == " AVAILABLE" ]]; then
    break
  fi
  sleep 57
done

echo Creating the OCI instance...
oci compute instance launch \
    --availability-domain $AD_NAME \
    --compartment-id $COMP_OCID \
    --image-id $IMAGE_OCID  \
    --shape $OCI_SHAPE      \
    --ssh-authorized-keys-file  ~/.ssh/oci_key_public.pem  \
    --subnet-id $SUBNET_OCID > /tmp/instance.out

