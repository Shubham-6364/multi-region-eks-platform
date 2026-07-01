import os

files = {}

# Backend
files['terraform/backend/main.tf'] = """
provider "aws" {
  region = "ap-south-1"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "mr-eks-prod-terraform-state-165044447471"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "terraform_lock" {
  name           = "mr-eks-prod-terraform-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
"""

# Root configs
files['terraform/versions.tf'] = """
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}
"""

files['terraform/providers.tf'] = """
provider "aws" {
  region = "ap-south-1"
  alias  = "primary"
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      Owner       = var.owner
      ManagedBy   = "Terraform"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  alias  = "secondary"

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      Owner       = var.owner
      ManagedBy   = "Terraform"
    }
  }
}
"""

files['terraform/variables.tf'] = """
variable "project_name" {
  type    = string
  default = "multi-region-eks"
}
variable "environment" {
  type    = string
  default = "prod"
}
variable "owner" {
  type    = string
  default = "devops"
}
variable "aws_account_id" {
  type    = string
  default = "165044447471"
}
variable "domain_name" {
  type    = string
  default = "k8s.codersdiary.online"
}
"""

# VPC Module
files['terraform/modules/vpc/main.tf'] = """
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.5.0"

  name = "${var.project_name}-${var.environment}-${var.region}-vpc"
  cidr = var.cidr

  azs             = var.azs
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets

  enable_nat_gateway = true
  single_nat_gateway = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
    "karpenter.sh/discovery"          = "${var.project_name}-${var.environment}-${var.region}"
  }
}
"""
files['terraform/modules/vpc/variables.tf'] = """
variable "project_name" {}
variable "environment" {}
variable "region" {}
variable "cidr" {}
variable "azs" { type = list(string) }
variable "private_subnets" { type = list(string) }
variable "public_subnets" { type = list(string) }
"""
files['terraform/modules/vpc/outputs.tf'] = """
output "vpc_id" { value = module.vpc.vpc_id }
output "private_subnets" { value = module.vpc.private_subnets }
output "public_subnets" { value = module.vpc.public_subnets }
"""

# EKS Module
files['terraform/modules/eks/main.tf'] = """
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.8.4"

  cluster_name    = "${var.project_name}-${var.environment}-${var.region}"
  cluster_version = "1.29"

  vpc_id                   = var.vpc_id
  subnet_ids               = var.private_subnets
  control_plane_subnet_ids = var.private_subnets

  cluster_endpoint_public_access = true

  enable_cluster_creator_admin_permissions = true

  eks_managed_node_groups = {
    initial = {
      instance_types = ["t3.medium"]
      min_size       = 2
      max_size       = 3
      desired_size   = 2
    }
  }

  node_security_group_tags = {
    "karpenter.sh/discovery" = "${var.project_name}-${var.environment}-${var.region}"
  }
}
"""
files['terraform/modules/eks/variables.tf'] = """
variable "project_name" {}
variable "environment" {}
variable "region" {}
variable "vpc_id" {}
variable "private_subnets" { type = list(string) }
"""
files['terraform/modules/eks/outputs.tf'] = """
output "cluster_name" { value = module.eks.cluster_name }
output "cluster_endpoint" { value = module.eks.cluster_endpoint }
output "cluster_certificate_authority_data" { value = module.eks.cluster_certificate_authority_data }
output "oidc_provider_arn" { value = module.eks.oidc_provider_arn }
output "node_security_group_id" { value = module.eks.node_security_group_id }
"""

# IAM Module (IRSA for ALB, ExternalDNS, CertManager)
files['terraform/modules/iam/main.tf'] = """
module "load_balancer_controller_irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "5.37.1"

  role_name                              = "${var.cluster_name}-alb-controller"
  attach_load_balancer_controller_policy = true

  oidc_providers = {
    ex = {
      provider_arn               = var.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
}

module "external_dns_irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "5.37.1"

  role_name                     = "${var.cluster_name}-external-dns"
  attach_external_dns_policy    = true
  external_dns_hosted_zone_arns = ["arn:aws:route53:::hostedzone/*"]

  oidc_providers = {
    ex = {
      provider_arn               = var.oidc_provider_arn
      namespace_service_accounts = ["kube-system:external-dns"]
    }
  }
}

module "cert_manager_irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "5.37.1"

  role_name                     = "${var.cluster_name}-cert-manager"
  attach_cert_manager_policy    = true
  cert_manager_hosted_zone_arns = ["arn:aws:route53:::hostedzone/*"]

  oidc_providers = {
    ex = {
      provider_arn               = var.oidc_provider_arn
      namespace_service_accounts = ["cert-manager:cert-manager"]
    }
  }
}
"""
files['terraform/modules/iam/variables.tf'] = """
variable "cluster_name" {}
variable "oidc_provider_arn" {}
"""
files['terraform/modules/iam/outputs.tf'] = """
output "alb_controller_role_arn" { value = module.load_balancer_controller_irsa_role.iam_role_arn }
output "external_dns_role_arn" { value = module.external_dns_irsa_role.iam_role_arn }
output "cert_manager_role_arn" { value = module.cert_manager_irsa_role.iam_role_arn }
"""

# Environments Prod - AP-South-1
files['terraform/environments/prod/ap-south-1/main.tf'] = """
terraform {
  backend "s3" {
    bucket         = "mr-eks-prod-terraform-state-165044447471"
    key            = "prod/ap-south-1/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "mr-eks-prod-terraform-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
}

module "vpc" {
  source          = "../../../modules/vpc"
  project_name    = var.project_name
  environment     = var.environment
  region          = var.region
  cidr            = var.vpc_cidr
  azs             = ["${var.region}a", "${var.region}b", "${var.region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.10.0/24", "10.0.20.0/24", "10.0.30.0/24"]
}

module "eks" {
  source          = "../../../modules/eks"
  project_name    = var.project_name
  environment     = var.environment
  region          = var.region
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
}

module "iam" {
  source            = "../../../modules/iam"
  cluster_name      = module.eks.cluster_name
  oidc_provider_arn = module.eks.oidc_provider_arn
}
"""
files['terraform/environments/prod/ap-south-1/variables.tf'] = """
variable "project_name" {}
variable "environment" {}
variable "region" {}
variable "vpc_cidr" {}
"""
files['terraform/environments/prod/ap-south-1/terraform.tfvars'] = """
project_name = "mr-eks"
environment  = "prod"
region       = "ap-south-1"
vpc_cidr     = "10.0.0.0/16"
"""

# Environments Prod - US-East-1
files['terraform/environments/prod/us-east-1/main.tf'] = """
terraform {
  backend "s3" {
    bucket         = "mr-eks-prod-terraform-state-165044447471"
    key            = "prod/us-east-1/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "mr-eks-prod-terraform-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
}

module "vpc" {
  source          = "../../../modules/vpc"
  project_name    = var.project_name
  environment     = var.environment
  region          = var.region
  cidr            = var.vpc_cidr
  azs             = ["${var.region}a", "${var.region}b", "${var.region}c"]
  private_subnets = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
  public_subnets  = ["10.1.10.0/24", "10.1.20.0/24", "10.1.30.0/24"]
}

module "eks" {
  source          = "../../../modules/eks"
  project_name    = var.project_name
  environment     = var.environment
  region          = var.region
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
}

module "iam" {
  source            = "../../../modules/iam"
  cluster_name      = module.eks.cluster_name
  oidc_provider_arn = module.eks.oidc_provider_arn
}
"""
files['terraform/environments/prod/us-east-1/variables.tf'] = """
variable "project_name" {}
variable "environment" {}
variable "region" {}
variable "vpc_cidr" {}
"""
files['terraform/environments/prod/us-east-1/terraform.tfvars'] = """
project_name = "mr-eks"
environment  = "prod"
region       = "us-east-1"
vpc_cidr     = "10.1.0.0/16"
"""

for filepath, content in files.items():
    # Make sure we don't try to write into non-existent directories. We already made them, but just in case.
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content.strip() + '\\n')
print("Terraform core files generated successfully!")
