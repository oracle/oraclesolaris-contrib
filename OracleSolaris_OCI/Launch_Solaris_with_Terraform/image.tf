# Retrieve the OCI Marketplace listings that have a name matching "Oracle Solaris"
data "oci_marketplace_listings" "solaris_listings" {
    compartment_id = var.compartment_ocid
    name = [var.listing_name]   # "Oracle Solaris 11.4"
}

# Select the first listing, because it will be the newest.
data "oci_marketplace_listing" "solaris_latest" {
  listing_id     = data.oci_marketplace_listings.solaris_listings.listings[0].id
  compartment_id = var.compartment_ocid
}

# Get the listing package associated with the listing and version already found.
data "oci_marketplace_listing_package" "solaris_list_pkg" {
  listing_id      = data.oci_marketplace_listing.solaris_latest.id
  package_version = data.oci_marketplace_listing.solaris_latest.default_package_version
}

# Get the list of listing packages associated with the listing and version already found.
data "oci_marketplace_listing_packages" "solaris_list_pkgs" {
  listing_id      = data.oci_marketplace_listing.solaris_latest.id
# package_version = data.oci_marketplace_listing.solaris_latest.default_package_version
}

# This is used when specifying the instance (in compute.tf).
data "oci_core_app_catalog_listing_resource_version" "solaris_catalog_listing" {
  listing_id = data.oci_marketplace_listing_package.solaris_list_pkg.app_catalog_listing_id
  resource_version = data.oci_marketplace_listing_package.solaris_list_pkg.app_catalog_listing_resource_version
}

# Retrieve any agreements needed, which match the listing found above.
data "oci_marketplace_listing_package_agreements" "solaris_list_pkg_agreements" {
    listing_id = data.oci_marketplace_listing.solaris_latest.id
    package_version = data.oci_marketplace_listing.solaris_latest.default_package_version
}



# Some OCI resources can only be used after you accept the terms and conditions. For the purposes
# of automation, that acceptance is implemented as an "accepted agreement". Within the Terraform
# OCI provider, two resources are used: the oci_marketplace_accepted_agreement and 
# oci_marketplace_listing_package_agreement.
resource "oci_marketplace_listing_package_agreement" "solaris_list_pkg_agreement" {
  agreement_id    = data.oci_marketplace_listing_package_agreements.solaris_list_pkg_agreements.agreements[0].id
  listing_id      = data.oci_marketplace_listing.solaris_latest.id
  package_version = data.oci_marketplace_listing.solaris_latest.default_package_version
}

resource "oci_marketplace_accepted_agreement" "solaris_accepted_agreement" {
  agreement_id    = oci_marketplace_listing_package_agreement.solaris_list_pkg_agreement.agreement_id
  compartment_id  = var.compartment_ocid
  listing_id      = data.oci_marketplace_listing.solaris_latest.id
  package_version = data.oci_marketplace_listing.solaris_latest.default_package_version
  signature       = oci_marketplace_listing_package_agreement.solaris_list_pkg_agreement.signature
}


# As well for every new Solaris release new subscription needs to be obtained in the Application Catalog
# (This needs to be done only once and could be done via GUI if needed)

# subscription details
resource "oci_core_app_catalog_listing_resource_version_agreement" "solaris_latest_catalog_details" {
  listing_id               = data.oci_core_app_catalog_listing_resource_version.solaris_catalog_listing.listing_id
  listing_resource_version = data.oci_core_app_catalog_listing_resource_version.solaris_catalog_listing.listing_resource_version
}

# signing subscription
resource "oci_core_app_catalog_subscription" "solaris_subscription" {
  compartment_id           = var.compartment_ocid
  listing_id               = oci_core_app_catalog_listing_resource_version_agreement.solaris_latest_catalog_details.listing_id
  listing_resource_version = oci_core_app_catalog_listing_resource_version_agreement.solaris_latest_catalog_details.listing_resource_version
  oracle_terms_of_use_link = oci_core_app_catalog_listing_resource_version_agreement.solaris_latest_catalog_details.oracle_terms_of_use_link
  signature                = oci_core_app_catalog_listing_resource_version_agreement.solaris_latest_catalog_details.signature
  time_retrieved           = oci_core_app_catalog_listing_resource_version_agreement.solaris_latest_catalog_details.time_retrieved
  eula_link                = oci_core_app_catalog_listing_resource_version_agreement.solaris_latest_catalog_details.eula_link

  // May take long for the subscription to propagate to all regions
  timeouts {
    create = "20m"
  }
}

