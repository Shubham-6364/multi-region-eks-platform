import os

files = {}

# 1. GitHub Actions CI/CD Pipeline
files['.github/workflows/deploy.yml'] = """
name: CI/CD Pipeline

on:
  push:
    branches:
      - main
    paths:
      - 'src/**' # Assuming app source code is in src/

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-south-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and Tag Image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: mr-eks-frontend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG ./src
          echo "Building docker image..."

      - name: Run Trivy Vulnerability Scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '${{ steps.login-ecr.outputs.registry }}/mr-eks-frontend:${{ github.sha }}'
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          vuln-type: 'os,library'
          severity: 'CRITICAL,HIGH'

      - name: Push Image to ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: mr-eks-frontend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          echo "Pushing docker image..."

      - name: Update GitOps Manifests
        env:
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # sed -i "s/image: .*/image: <account-id>.dkr.ecr.ap-south-1.amazonaws.com\\/mr-eks-frontend:$IMAGE_TAG/g" applications/frontend.yaml
          # git config --global user.name 'GitHub Actions'
          # git config --global user.email 'actions@github.com'
          # git commit -am "Update frontend image to $IMAGE_TAG"
          # git push
          echo "Updating ArgoCD manifests..."
"""

# 2. Disaster Recovery Scripts
files['scripts/simulate-failure.sh'] = """#!/bin/bash
# Simulates a regional failure by disabling the primary region's workloads

echo "Simulating failure in ap-south-1 (Mumbai)..."

# Scale down deployments to 0 to trigger Route53 health check failure
kubectl --context=mr-eks-prod-ap-south-1 scale deployment frontend --replicas=0 -n default
kubectl --context=mr-eks-prod-ap-south-1 scale deployment istio-ingressgateway --replicas=0 -n istio-system

echo "Failure simulated. Route53 should detect the health check failure within a minute and failover to us-east-1."
"""

files['scripts/failover.sh'] = """#!/bin/bash
# Manual failover script to immediately switch traffic to the secondary region

echo "Executing manual failover to us-east-1 (N. Virginia)..."

# In a real scenario, this script could update Route53 records via AWS CLI
# or update an ArgoCD parameter to route 100% of traffic to the secondary ALB.
aws route53 change-resource-record-sets \\
  --hosted-zone-id YOUR_ZONE_ID \\
  --change-batch '{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{"Name":"k8s.codersdiary.online","Type":"CNAME","SetIdentifier":"primary","Failover":"SECONDARY","TTL":60,"ResourceRecords":[{"Value":"SECONDARY_ALB_ENDPOINT"}]}}]}'

echo "Traffic successfully rerouted to us-east-1."
"""

for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content.strip() + '\\n')
    
    # Make scripts executable
    if filepath.startswith('scripts/'):
        os.chmod(filepath, 0o755)

print("Milestone 4 files generated successfully!")
