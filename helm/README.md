# Helm Directory

Contains custom Helm charts, values files, and packaging for both infrastructure add-ons (like Istio, ExternalDNS, Karpenter) and custom microservices.

## Interconnection
- Values and templates here are consumed by ArgoCD applications defined in `gitops/`.
- Provides the parameterized deployment packages that make multi-region and multi-environment deployments consistent.
