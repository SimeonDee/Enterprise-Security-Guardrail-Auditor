# ─────────────────────────────────────────────────────────────
# Sample Terraform Configuration — Multi-Service Vulnerable
# Purpose: Testing & validation of the Enterprise Security
#          Guardrail Auditor scanner engine (sample 2).
#
# DO NOT deploy this configuration. It contains deliberate
# security misconfigurations for demonstration purposes.
# ─────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}

# ─── FINDING: S3_PUBLIC_ACCESS (Critical) ───────────────────
# Authenticated-read still leaks data to any AWS account
resource "aws_s3_bucket" "website_assets" {
  bucket = "globex-website-assets"
  acl    = "authenticated-read"

  tags = {
    Project = "marketing-site"
  }
}

# Clean bucket — versioning enabled, private
resource "aws_s3_bucket" "terraform_state" {
  bucket = "globex-tfstate-eu"
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Purpose = "terraform-state"
  }
}

# ─── FINDING: SG_OPEN_SSH (Critical) ───────────────────────
# Wide port range that includes SSH
resource "aws_security_group" "dev_access" {
  name        = "dev-wide-open"
  description = "Development access with overly broad ports"
  vpc_id      = "vpc-0fedcba987654321"

  ingress {
    description = "All common ports"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = "development"
  }
}

# ─── FINDING: SG_OPEN_SSH (Critical) ───────────────────────
# Security group rule resource with SSH open
resource "aws_security_group_rule" "bastion_ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "sg-0abc123456789"
}

# Clean SG rule — restricted CIDR
resource "aws_security_group_rule" "office_ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["192.168.1.0/24"]
  security_group_id = "sg-0abc123456789"
}

# ─── FINDING: DB_PUBLIC_ACCESS (Critical) ──────────────────
# Aurora cluster exposed to the internet
resource "aws_rds_cluster" "reporting" {
  cluster_identifier  = "globex-reporting-cluster"
  engine              = "aurora-mysql"
  engine_version      = "8.0.mysql_aurora.3.04.0"
  master_username     = "report_admin"
  master_password     = "Reporting2026!"
  publicly_accessible = true
  storage_encrypted   = true
  skip_final_snapshot = true

  tags = {
    Team = "business-intelligence"
  }
}

# ─── FINDING: ENCRYPTION_DISABLED (High) ──────────────────
# Large unencrypted data warehouse volume
resource "aws_ebs_volume" "warehouse_storage" {
  availability_zone = "eu-west-1b"
  size              = 2000
  type              = "gp3"
  encrypted         = false

  tags = {
    Name    = "data-warehouse-vol"
    Purpose = "analytics"
  }
}

# ─── FINDING: ENCRYPTION_DISABLED (High) ──────────────────
# MySQL instance without encryption
resource "aws_db_instance" "legacy_app_db" {
  identifier          = "globex-legacy-mysql"
  engine              = "mysql"
  engine_version      = "8.0.35"
  instance_class      = "db.r6g.large"
  allocated_storage   = 200
  publicly_accessible = false
  storage_encrypted   = false
  multi_az            = true
  skip_final_snapshot = true

  tags = {
    Application = "legacy-erp"
  }
}

# Clean DB — encrypted and private
resource "aws_db_instance" "new_app_db" {
  identifier          = "globex-new-api-db"
  engine              = "postgres"
  engine_version      = "16.1"
  instance_class      = "db.t4g.medium"
  allocated_storage   = 50
  publicly_accessible = false
  storage_encrypted   = true
  skip_final_snapshot = true
}

# ─── FINDING: IAM_WILDCARD (Critical) ─────────────────────
# User policy with wildcard actions on all S3
resource "aws_iam_user_policy" "dev_s3_full" {
  name = "dev-s3-full-access"
  user = "developer-jane"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "arn:aws:s3:::*"
    }
  ]
}
EOF
}

# ─── FINDING: IAM_WILDCARD (Critical) ─────────────────────
# Group policy granting full admin
resource "aws_iam_group_policy" "ops_full_access" {
  name  = "ops-unrestricted"
  group = "operations-team"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "FullAccess",
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
EOF
}

# Clean IAM — scoped permissions
resource "aws_iam_policy" "cloudwatch_readonly" {
  name        = "CloudWatchReadOnly"
  description = "Read-only access to CloudWatch metrics and logs"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricData",
        "cloudwatch:ListMetrics",
        "logs:GetLogEvents",
        "logs:DescribeLogGroups"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

# ─── Seed guardrail triggers ──────────────────────────────

# Overly permissive egress (seed rule)
resource "aws_security_group" "wide_egress" {
  name   = "allow-all-egress"
  vpc_id = "vpc-0fedcba987654321"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Default VPC usage (seed rule)
resource "aws_default_vpc" "eu_default" {
  tags = {
    Name = "EU Default VPC — should not be used"
  }
}
