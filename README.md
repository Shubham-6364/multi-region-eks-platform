# Multi-Region EKS Platform

A production-grade multi-region Kubernetes platform on AWS EKS with automated cross-region failover, Istio service mesh, and centralized observability.

## Project Structure Overview

Our platform is organized into the following key modules:

- **`terraform/`**: Infrastructure as Code (IaC) to provision the foundational AWS resources (VPCs, EKS clusters, IAM, DynamoDB, S3) across multiple regions and environments.
- **`gitops/`**: The ArgoCD source of truth that continuously syncs the cluster state with this repository.
- **`applications/`**: Kubernetes manifests and configurations for the microservices deployed on the platform.
- **`helm/`**: Custom Helm charts and configuration values for cluster add-ons and applications.
- **`scripts/`**: Automation utilities for bootstrapping, CI/CD, and failure testing.
- **`.github/`**: GitHub Actions workflows for continuous integration and continuous deployment (CI/CD).
- **`docs/`**: Comprehensive runbooks, setup guides, and operational documentation.
- **`diagrams/`**: Visual representations of the architecture and traffic flow.

## Interconnections

1. **Provisioning**: `terraform/` creates the multi-region clusters and necessary AWS roles (IRSA).
2. **Bootstrapping**: `scripts/` initializes ArgoCD into the newly created clusters.
3. **Reconciliation**: ArgoCD watches `gitops/` to deploy add-ons and `applications/`.
4. **Configuration**: `gitops/` apps heavily rely on parameterized charts stored in `helm/`.
5. **Automation**: `.github/` workflows run tests, build images, and update manifests in `gitops/` to trigger deployments.