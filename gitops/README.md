# GitOps Directory

This directory is the single source of truth for the cluster state, managed by ArgoCD. 
It defines the desired state of our applications, add-ons, and infrastructure components within the Kubernetes clusters.

## Interconnection
- Watches the `applications/` and `helm/` directories to deploy workloads.
- Synchronizes with our AWS infrastructure provisioned via the `terraform/` directory.
- ArgoCD continuously reconciles the cluster state with the configurations defined here.
