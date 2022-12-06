# These data objects are used to display the objects' names.
data "oci_core_subnet" "mysubnet" {
  subnet_id = var.subnet_id
}

data "oci_core_vcn" "myvcn" {
  vcn_id = data.oci_core_subnet.mysubnet.vcn_id
}

data "oci_identity_compartment" "mycompartment" {
  id = var.compartment_ocid
}

