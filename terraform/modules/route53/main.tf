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
}\n