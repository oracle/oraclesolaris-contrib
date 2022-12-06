variable "region" {
    default = "us-phoenix-1"
}

variable "availability_domain" {
  default = "ruWb:PHX-AD-1"
}

variable "compartment_ocid" {  
  default = "ocid1.compartment.oc1..aaa..."
}

variable "subnet_id" {
  default = "ocid1.subnet.oc1.phx.aa..."
}

# The next set of variables specify the instance to be created.
variable "listing_name" {
  default = "Oracle Solaris 11.4"
}

variable "instance_shape" { 
  default = "VM.Standard2.1"
}   

variable "boot_volume_size" {
  default = "50"
}

variable "instance_display_name" {
  default = "Oracle Solaris 11.4"
}

variable "ssh_public_key_path" {
  description = "SSH Public Key Path"
  default = "/.../.../.ssh/ocisshkey.pub"
}

