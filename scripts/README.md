# Scripts Directory

Utility scripts for automation, CI/CD pipelines, bootstrapping, and disaster recovery testing.

## Interconnection
- Called by GitHub Actions workflows in `.github/workflows/`.
- Used to bootstrap the initial cluster state before ArgoCD takes over.
- Scripts may interact with AWS resources created by `terraform/`.
