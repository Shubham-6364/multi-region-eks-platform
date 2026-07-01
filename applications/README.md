# Applications Directory

This directory contains the Kubernetes manifests and configurations for the microservices and user-facing applications deployed on the EKS platform.

## Interconnection
- Deployed automatically via **ArgoCD** through the `gitops/` configuration.
- Applications here may reference Helm charts from the `helm/` directory.
- Relies on infrastructure like Route53, ALBs, and databases provisioned in `terraform/`.
