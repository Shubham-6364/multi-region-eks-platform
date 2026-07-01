import os

files = {}

# 1. Applications (Sample Microservices)
files['applications/frontend.yaml'] = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
        sidecar.istio.io/inject: "true"
    spec:
      containers:
      - name: frontend
        image: nginx:alpine
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: default
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: istio
    cert-manager.io/cluster-issuer: letsencrypt-prod
    external-dns.alpha.kubernetes.io/hostname: k8s.codersdiary.online
spec:
  tls:
  - hosts:
    - k8s.codersdiary.online
    secretName: frontend-tls
  rules:
  - host: k8s.codersdiary.online
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
"""

# 2. GitOps Application definitions
files['gitops/applications/frontend.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: frontend-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/Codersdiary/multi-region-eks-platform.git'
    path: applications
    targetRevision: HEAD
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
"""

# 3. Observability (Prometheus & Grafana)
files['gitops/add-ons/kube-prometheus-stack.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kube-prometheus-stack
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://prometheus-community.github.io/helm-charts'
    targetRevision: 58.2.1
    chart: kube-prometheus-stack
    helm:
      valueFiles:
        - https://raw.githubusercontent.com/Codersdiary/multi-region-eks-platform/main/helm/kube-prometheus-stack/values.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: monitoring
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
"""

# Logging (Loki Stack)
files['gitops/add-ons/loki-stack.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: loki-stack
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://grafana.github.io/helm-charts'
    targetRevision: 2.10.1
    chart: loki-stack
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: logging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
"""

files['helm/kube-prometheus-stack/values.yaml'] = """
grafana:
  enabled: true
  ingress:
    enabled: true
    ingressClassName: istio
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt-prod
    hosts:
      - grafana.k8s.codersdiary.online
    tls:
      - secretName: grafana-tls
        hosts:
          - grafana.k8s.codersdiary.online
"""

# 4. Terraform Route53 Failover Module
files['terraform/modules/route53/main.tf'] = """
data "aws_route53_zone" "this" {
  name = var.domain_name
}

resource "aws_route53_health_check" "primary" {
  fqdn              = var.primary_endpoint
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = "3"
  request_interval  = "30"
}

resource "aws_route53_record" "primary" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = var.record_name
  type    = "CNAME"
  ttl     = "60"

  failover_routing_policy {
    type = "PRIMARY"
  }

  set_identifier = "primary"
  records        = [var.primary_endpoint]
  health_check_id = aws_route53_health_check.primary.id
}

resource "aws_route53_record" "secondary" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = var.record_name
  type    = "CNAME"
  ttl     = "60"

  failover_routing_policy {
    type = "SECONDARY"
  }

  set_identifier = "secondary"
  records        = [var.secondary_endpoint]
}
"""

files['terraform/modules/route53/variables.tf'] = """
variable "domain_name" {}
variable "record_name" {}
variable "primary_endpoint" {}
variable "secondary_endpoint" {}
"""

for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content.strip() + '\\n')
print("Milestone 3 files generated successfully!")
