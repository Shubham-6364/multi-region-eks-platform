variable "project_name" {}
variable "environment" {}
variable "region" {}
variable "cidr" {}
variable "azs" { type = list(string) }
variable "private_subnets" { type = list(string) }
variable "public_subnets" { type = list(string) }\n