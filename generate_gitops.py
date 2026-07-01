import os

files = {}

# 1. Bootstrap App of Apps
files['gitops/bootstrap/addons-app.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cluster-addons
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/Codersdiary/multi-region-eks-platform.git'
    path: gitops/add-ons
    targetRevision: HEAD
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
"""

# 2. Add-on Apps
files['gitops/add-ons/metrics-server.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: metrics-server
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://kubernetes-sigs.github.io/metrics-server/'
    targetRevision: 3.12.1
    chart: metrics-server
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: kube-system
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
"""

files['gitops/add-ons/aws-load-balancer-controller.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: aws-load-balancer-controller
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://aws.github.io/eks-charts'
    targetRevision: 1.7.2
    chart: aws-load-balancer-controller
    helm:
      valueFiles:
        - https://raw.githubusercontent.com/Codersdiary/multi-region-eks-platform/main/helm/aws-load-balancer-controller/values.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: kube-system
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
"""

files['gitops/add-ons/external-dns.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: external-dns
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://kubernetes-sigs.github.io/external-dns/'
    targetRevision: 1.14.4
    chart: external-dns
    helm:
      valueFiles:
        - https://raw.githubusercontent.com/Codersdiary/multi-region-eks-platform/main/helm/external-dns/values.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: kube-system
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
"""

files['gitops/add-ons/cert-manager.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cert-manager
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://charts.jetstack.io'
    targetRevision: v1.14.4
    chart: cert-manager
    helm:
      valueFiles:
        - https://raw.githubusercontent.com/Codersdiary/multi-region-eks-platform/main/helm/cert-manager/values.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: cert-manager
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
"""

files['gitops/add-ons/karpenter.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: karpenter
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'oci://public.ecr.aws/karpenter/karpenter'
    targetRevision: 0.36.2
    chart: karpenter
    helm:
      valueFiles:
        - https://raw.githubusercontent.com/Codersdiary/multi-region-eks-platform/main/helm/karpenter/values.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: kube-system
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
"""

files['gitops/add-ons/istio-base.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: istio-base
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://istio-release.storage.googleapis.com/charts'
    targetRevision: 1.22.0
    chart: base
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: istio-system
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
"""

files['gitops/add-ons/istiod.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: istiod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://istio-release.storage.googleapis.com/charts'
    targetRevision: 1.22.0
    chart: istiod
    helm:
      valueFiles:
        - https://raw.githubusercontent.com/Codersdiary/multi-region-eks-platform/main/helm/istio/values.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: istio-system
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
"""

files['gitops/add-ons/custom-manifests.yaml'] = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: custom-manifests
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/Codersdiary/multi-region-eks-platform.git'
    path: gitops/manifests
    targetRevision: HEAD
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: cert-manager
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
"""

# 3. Helm Values
files['helm/aws-load-balancer-controller/values.yaml'] = """
clusterName: mr-eks-prod-ap-south-1
serviceAccount:
  create: false
  name: aws-load-balancer-controller
"""

files['helm/external-dns/values.yaml'] = """
provider: aws
domainFilters:
  - k8s.codersdiary.online
serviceAccount:
  create: false
  name: external-dns
"""

files['helm/cert-manager/values.yaml'] = """
installCRDs: true
serviceAccount:
  create: false
  name: cert-manager
"""

files['gitops/manifests/cluster-issuer.yaml'] = """
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: play.video2525@gmail.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: istio
"""

files['helm/karpenter/values.yaml'] = """
settings:
  clusterName: mr-eks-prod-ap-south-1
serviceAccount:
  create: false
  name: karpenter
"""

files['helm/istio/values.yaml'] = """
meshConfig:
  accessLogFile: /dev/stdout
  defaultConfig:
    proxyMetadata:
      ISTIO_META_DNS_CAPTURE: "true"
"""

for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content.strip() + '\\n')
print("Milestone 2 GitOps files generated successfully!")
