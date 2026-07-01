#!/bin/bash
# Simulates a regional failure by disabling the primary region's workloads

echo "Simulating failure in ap-south-1 (Mumbai)..."

# Scale down deployments to 0 to trigger Route53 health check failure
kubectl --context=mr-eks-prod-ap-south-1 scale deployment frontend --replicas=0 -n default
kubectl --context=mr-eks-prod-ap-south-1 scale deployment istio-ingressgateway --replicas=0 -n istio-system

echo "Failure simulated. Route53 should detect the health check failure within a minute and failover to us-east-1."\n