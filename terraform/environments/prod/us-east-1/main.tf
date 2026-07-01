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
}\n