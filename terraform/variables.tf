#Region to use, defaults to USE1 for sandbox.
variable "region" {
    default = "us-east-1"
}

variable "cost_center" {
    description = "The LOWER_CASE cost center to associate this instance with. Used for tagging and access permissions, will be part of your Role Name (ie DEMM Poweruser is demm)"
    default = "scff"
}

variable "owner_email" {
    description = "Your email address, so we can hunt you down. NOTE: leaving this as unbound dl for more contacts"
    default = "DL-Unbound-Boston-Brains@chewy.com"
}

variable "data_classification" {
    description = "Your data classification for this instance. As this is a sandbox helper, this had BETTER NOT BE PII."
    default = "internal"
}

variable "app_name" {
    description = "What to name your stuff"
    default = "storefront-chatbot"
}

variable "environment" {
    description = "What environment is this deploying into. This had better be sandbox. sbx->dev"
    default = "dev"
}

variable "instance_type" {
    description = "What instance class to use"
    default = "t3.large"
}