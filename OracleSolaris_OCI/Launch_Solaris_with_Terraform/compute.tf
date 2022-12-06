## Specify the Oracle Solaris instance to be created.
resource "oci_core_instance" "solaris_instance" {
  availability_domain = var.availability_domain
  compartment_id = var.compartment_ocid
  shape = var.instance_shape
  source_details {
      source_type = "image"
      # The image ID is determined in image.tf 
      source_id = data.oci_core_app_catalog_listing_resource_version.solaris_catalog_listing.listing_resource_id
  }

  display_name = var.instance_display_name
  create_vnic_details {
      assign_public_ip = true
      subnet_id = var.subnet_id
  }
  metadata = {
      ssh_authorized_keys = file(var.ssh_public_key_path)
  } 
  preserve_boot_volume = false
}


