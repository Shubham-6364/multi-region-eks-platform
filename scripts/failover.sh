#!/bin/bash
# Manual failover script to immediately switch traffic to the secondary region

echo "Executing manual failover to us-east-1 (N. Virginia)..."

# In a real scenario, this script could update Route53 records via AWS CLI
# or update an ArgoCD parameter to route 100% of traffic to the secondary ALB.
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch '{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{"Name":"k8s.codersdiary.online","Type":"CNAME","SetIdentifier":"primary","Failover":"SECONDARY","TTL":60,"ResourceRecords":[{"Value":"SECONDARY_ALB_ENDPOINT"}]}}]}'

echo "Traffic successfully rerouted to us-east-1."\n