output "alb_controller_role_arn" { value = module.load_balancer_controller_irsa_role.iam_role_arn }
output "external_dns_role_arn" { value = module.external_dns_irsa_role.iam_role_arn }
output "cert_manager_role_arn" { value = module.cert_manager_irsa_role.iam_role_arn }\n