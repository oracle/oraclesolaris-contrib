output "A01_Compartment-Name" {
  value = data.oci_identity_compartment.mycompartment.name
}

output "A01_Subnet-OCID" {
  value = var.subnet_id
}

output "A02_Shape-of-Instance" {
  value = oci_core_instance.solaris_instance.shape
}
output "A03_OCPUS" {
  value = oci_core_instance.solaris_instance.shape_config[0].ocpus
}
output "A04_RAM_GB" {
  value = oci_core_instance.solaris_instance.shape_config[0].memory_in_gbs
}
output "A05_Boot_Vol_GB" {
  value = oci_core_instance.solaris_instance.source_details[0].boot_volume_size_in_gbs
}
output "A_END" {
  value = "===================="
}

output "B1_query_name" {
  value = var.listing_name
}
output "B2_solaris_listings_length" {
  value = length(data.oci_marketplace_listings.solaris_listings.listings)
}
output "B3_solaris_listings-0-id" {
  value = data.oci_marketplace_listings.solaris_listings.listings[0].id
}
output "B4_solaris_listings-0-default_package_version" {
  value = data.oci_marketplace_listings.solaris_listings.listings[0].default_package_version
}
output "B_END" {
  value = "===================="
}

output "D1_solaris_marketplace_list_package-id" {
  value = data.oci_marketplace_listing_package.solaris_list_pkg.id
}
output "D2_solaris_marketplace_list_package-app_catalog_listing_resource_version" {
  value = data.oci_marketplace_listing_package.solaris_list_pkg.app_catalog_listing_resource_version
}
output "D3_solaris_marketplace_list_package-image_id" {
  value = data.oci_marketplace_listing_package.solaris_list_pkg.image_id
}
output "D4_solaris_marketplace_list_package-listing_id" {
  value = data.oci_marketplace_listing_package.solaris_list_pkg.listing_id
}
output "D5_solaris_marketplace_list_package-resource_id" {
  value = data.oci_marketplace_listing_package.solaris_list_pkg.resource_id
}
output "D6_solaris_marketplace_list_package-time_created" {
  value = data.oci_marketplace_listing_package.solaris_list_pkg.time_created
}
output "D7_solaris_marketplace_list_package-package_version" {
  value = data.oci_marketplace_listing_package.solaris_list_pkg.package_version
}
output "D8_solaris_marketplace_list_package-version" {
  value = data.oci_marketplace_listing_package.solaris_list_pkg.version
}
output "D9_solaris_marketplace_list_package-additional_info" {
  value = "This object also includes pricing information."
}
output "D_END" {
  value = "===================="
}

output "E1_oci_core_app_catalog_listing_resource_version-id" {
  value = data.oci_core_app_catalog_listing_resource_version.solaris_catalog_listing.id
}
output "E2_oci_core_app_catalog_listing_resource_version-listing_id" {
  value = data.oci_core_app_catalog_listing_resource_version.solaris_catalog_listing.listing_id
}
output "E3_oci_core_app_catalog_listing_resource_version-listing_resource_version" {
  value = data.oci_core_app_catalog_listing_resource_version.solaris_catalog_listing.listing_resource_version
}
output "E4_oci_core_app_catalog_listing_resource_version-resource_version" {
  value = data.oci_core_app_catalog_listing_resource_version.solaris_catalog_listing.resource_version
}
output "E5_oci_core_app_catalog_listing_resource_version-additional_info" {
  value = "This object also includes lists of available_regions and compatible_shapes"
}
output "E_END" {
  value = "===================="
}


output "F1_solaris_list_pkg_agreements-0-id" {
  value = data.oci_marketplace_listing_package_agreements.solaris_list_pkg_agreements.agreements[0].id
}
output "F2_solaris_list_pkg_agreements-0-prompt" {
  value = substr(data.oci_marketplace_listing_package_agreements.solaris_list_pkg_agreements.agreements[0].prompt, 0, 80)
}
output "F_END" {
  value = "===================="
}

output "G1_solaris_list_pkg_agreement-agreement_id" {
  value = oci_marketplace_listing_package_agreement.solaris_list_pkg_agreement.agreement_id
}
output "G2_solaris_list_pkg_agreement-id" {
  value = oci_marketplace_listing_package_agreement.solaris_list_pkg_agreement.id
}
output "G3_solaris_list_pkg_agreement-listing_id" {
  value = oci_marketplace_listing_package_agreement.solaris_list_pkg_agreement.listing_id
}
output "G4_solaris_list_pkg_agreement-package_version" {
  value = oci_marketplace_listing_package_agreement.solaris_list_pkg_agreement.package_version
}
output "G5_solaris_list_pkg_agreement-signature" {
  value = oci_marketplace_listing_package_agreement.solaris_list_pkg_agreement.signature
}
output "G_END" {
  value = "===================="
}


