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
      instance_types = ["c7i-flex.large"]
      min_size       = 1
      max_size       = 1
      desired_size   = 1
    }
  }

  node_security_group_tags = {
    "karpenter.sh/discovery" = "${var.project_name}-${var.environment}-${var.region}"
  }
}\n