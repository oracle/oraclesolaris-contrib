# Launching an Oracle Solaris instance using Terraform

One of the [many methods that you can use to create an Oracle Solaris instance](https://blogs.oracle.com/solaris/post/oracle-solaris-shines-through-the-cloud) in [Oracle Cloud Infrastructure](https://www.oracle.com/a/ocom/docs/cloud/oracle-cloud-infrastructure-platform-overview-wp.pdf) leverages the popular [Terraform](https://www.terraform.io/) "Infrastructure-as-Code" tool. If you have used Terraform to create cloud instances running another operating system, you will find the Terraform code for Oracle Solaris to be very familiar. The explanation in this blog entry assumes that you are familiar with cloud computing, IaaS, Terraform, and OCI concepts including the ones we described in [our earlier entry describing OCI Marketplace automation](https://blogs.oracle.com/solaris/post/oracle-solaris-on-oci-marketplace-components).

The code at [our github site](https://github.com/oracle/oraclesolaris-contrib/tree/master/OracleSolaris_OCI) includes these three simple files with infrastructure code that will look familiar to Terraform users:
1. provider.tf specifies the Terraform OCI provider.
2. variables.tf specifies the usual site-specific information such as compartment and subnet. It also includes the name of the image that we want to boot, which is "Oracle Solaris 11.4".
3. compute.tf specifies the configuration of the OCI compute instance. The only line in this file which is not common to most types of instances is the specification of the *source_id*. This is described in the explanation of the file image.tf.

The only potential significant differences are automatically finding the OCI package we want, and the need to automatically accept the Terms of Use. The latter concepts were described in a [recent blog entry](https://blogs.oracle.com/solaris/post/oracle-solaris-on-oci-marketplace-components). Let's look at the Terraform code that achieves these two purposes.

The first Terraform block (below) looks through the OCI marketplace listings for entries with names that match "Oracle Solaris 11.4". These listings are sorted, by default, in reverse chronological order. The second block stores the OCID of the most recent version of Oracle Solaris, which is the first one.

```
# Retrieve the OCI Marketplace listings that have a name matching "Oracle Solaris"
data "oci_marketplace_listings" "solaris_listings" {
    compartment_id = var.compartment_ocid
    name = [var.listing_name]                # "Oracle Solaris 11.4"
}

# Select the first listing, because it will be the newest.
data "oci_marketplace_listing" "solaris_listing" {
  listing_id     = data.oci_marketplace_listings.solaris_listings.listings[0].id   # Latest version
  compartment_id = var.compartment_ocid
}
```

The third Terraform block maps the listing to the specific version of a listing package. The fourth block (*oci_core_app_catalog_listing_resource_version.solaris_catalog_listing*) maps that listing package to a catalog listing. That catalog listing includes a resource ID, which is the OCID of the OS image that we want to boot.

```
# Get the listing package associated with the listing and version already found.
data "oci_marketplace_listing_package" "solaris_list_pkg" {
  listing_id      = data.oci_marketplace_listing.solaris_listing.id
  package_version = data.oci_marketplace_listing.solaris_listing.default_package_version
}

# This block retrieves and stores the internal representation of the version of the OS package.
# It is used in compute.tf when specifying the instance.
data "oci_core_app_catalog_listing_resource_version" "solaris_catalog_listing" {
  listing_id = data.oci_marketplace_listing_package.solaris_list_pkg.app_catalog_listing_id
  resource_version = data.oci_marketplace_listing_package.solaris_list_pkg.app_catalog_listing_resource_version
}
```

The fifth block retrieves the list of agreements ("Terms of Use") associated with this version of this package. The user must agree to these. When using the Cloud Console, these appear in the web browser when you select an image.

```
# Retrieve any agreements needed, which match the listing found above.
data "oci_marketplace_listing_package_agreements" "solaris_list_pkg_agreements" {
    listing_id = data.oci_marketplace_listing.solaris_listing.id
    package_version = data.oci_marketplace_listing.solaris_listing.default_package_version
}
```

We know that there is only one agreement, so when we generate the *oci_marketplace_listing_package_agreement*resource in the next block, for simplicity we use the first one. The object that's retrieved by the next block includes a unique signature supplied by OCI, which you will send back to "sign" the agreement.

```
resource "oci_marketplace_listing_package_agreement" "solaris_list_pkg_agreement" {
  agreement_id    = data.oci_marketplace_listing_package_agreements.solaris_list_pkg_agreements.agreements[0].id
  listing_id      = data.oci_marketplace_listing.solaris_listing.id
  package_version = data.oci_marketplace_listing.solaris_listing.default_package_version
}
```

That signature, and related information, are used to automatically accept the Terms of Use in the final block.

```
resource "oci_marketplace_accepted_agreement" "solaris_accepted_agreement" {
  agreement_id    = oci_marketplace_listing_package_agreement.solaris_list_pkg_agreement.agreement_id
  compartment_id  = var.compartment_ocid
  listing_id      = data.oci_marketplace_listing.solaris_listing.id
  package_version = data.oci_marketplace_listing.solaris_listing.default_package_version
  signature       = oci_marketplace_listing_package_agreement.solaris_list_pkg_agreement.signature
}
```

Finally, the file outputs.tf reports to you the compartment and subnet where the instance was created, along with other useful information.

Copyright (c) 2022, Oracle and/or its affiliates. Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/. 