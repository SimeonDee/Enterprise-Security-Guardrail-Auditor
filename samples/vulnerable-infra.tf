# ─────────────────────────────────────────────────────────────
# Sample Terraform Configuration — Intentionally Vulnerable
# Purpose: Testing & validation of the Enterprise Security
#          Guardrail Auditor scanner engine.
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
  region = "us-east-1"
}

# ─── FINDING: S3_PUBLIC_ACCESS (Critical) ───────────────────
# Public ACL on S3 bucket exposes data to the internet
resource "aws_s3_bucket" "public_data" {
  bucket = "acme-corp-public-data-2026"
  acl    = "public-read"

  tags = {
    Environment = "production"
    Team        = "data-engineering"
  }
}

# ─── FINDING: S3_PUBLIC_ACCESS (Critical) ───────────────────
# Public-read-write is even more dangerous
resource "aws_s3_bucket" "upload_bucket" {
  bucket = "acme-corp-user-uploads"
  acl    = "public-read-write"

  tags = {
    Environment = "staging"
  }
}

# Clean bucket — should NOT trigger a finding
resource "aws_s3_bucket" "private_logs" {
  bucket = "acme-corp-audit-logs"
  acl    = "private"

  tags = {
    Environment = "production"
  }
}

# ─── FINDING: SG_OPEN_SSH (Critical) ───────────────────────
# SSH open to the world
resource "aws_security_group" "allow_all_ssh" {
  name        = "allow-ssh-anywhere"
  description = "Allow SSH from anywhere"
  vpc_id      = "vpc-0abc123def456789"

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "open-ssh-sg"
  }
}

# Clean security group — should NOT trigger a finding
resource "aws_security_group" "restricted_ssh" {
  name        = "restricted-ssh"
  description = "SSH from office only"
  vpc_id      = "vpc-0abc123def456789"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}

# ─── FINDING: DB_PUBLIC_ACCESS (Critical) ──────────────────
# Database publicly accessible
resource "aws_db_instance" "main_db" {
  identifier           = "acme-production-db"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.medium"
  allocated_storage    = 100
  db_name              = "acme_prod"
  username             = "admin"
  password             = "SuperSecret123!"
  publicly_accessible  = true
  skip_final_snapshot  = true
  storage_encrypted    = false

  tags = {
    Environment = "production"
  }
}
# ─── FINDING: ENCRYPTION_DISABLED (High) on same resource ─
# storage_encrypted = false is also flagged above

# ─── FINDING: DB_PUBLIC_ACCESS (Critical) ──────────────────
# RDS cluster publicly accessible
resource "aws_rds_cluster" "analytics_cluster" {
  cluster_identifier  = "acme-analytics"
  engine              = "aurora-postgresql"
  master_username     = "analytics_admin"
  master_password     = "AnotherSecret456!"
  publicly_accessible = true
  storage_encrypted   = false
  skip_final_snapshot = true
}
# ─── FINDING: ENCRYPTION_DISABLED (High) on same resource ─

# Clean database — should NOT trigger a finding
resource "aws_db_instance" "internal_db" {
  identifier          = "acme-internal-db"
  engine              = "mysql"
  engine_version      = "8.0"
  instance_class      = "db.t3.small"
  allocated_storage   = 50
  publicly_accessible = false
  storage_encrypted   = true
  skip_final_snapshot = true
}

# ─── FINDING: ENCRYPTION_DISABLED (High) ──────────────────
# EBS volume without encryption
resource "aws_ebs_volume" "data_volume" {
  availability_zone = "us-east-1a"
  size              = 500
  encrypted         = false

  tags = {
    Name = "unencrypted-data-vol"
  }
}

# Clean EBS — should NOT trigger a finding
resource "aws_ebs_volume" "encrypted_volume" {
  availability_zone = "us-east-1a"
  size              = 100
  encrypted         = true
}

# ─── FINDING: IAM_WILDCARD (Critical) ─────────────────────
# Wildcard action and resource — god-mode policy
resource "aws_iam_policy" "admin_policy" {
  name        = "FullAdminAccess"
  description = "Unrestricted admin access"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
EOF
}

# ─── FINDING: IAM_WILDCARD (Critical) ─────────────────────
# Wildcard on a role policy
resource "aws_iam_role_policy" "lambda_overreach" {
  name = "lambda-too-much-access"
  role = "lambda-execution-role"

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

# Clean IAM — should NOT trigger a finding
resource "aws_iam_policy" "read_only_s3" {
  name = "S3ReadOnly"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::acme-corp-audit-logs",
        "arn:aws:s3:::acme-corp-audit-logs/*"
      ]
    }
  ]
}
EOF
}

# ─── Additional resources for seed guardrail regex rules ───

# Default VPC usage (seed rule: Default VPC Usage)
resource "aws_default_vpc" "default" {
  tags = {
    Name = "Default VPC"
  }
}

# Missing backup (seed rule: Missing Backup Configuration)
resource "aws_db_instance" "no_backup_db" {
  identifier              = "acme-no-backup"
  engine                  = "postgres"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  backup_retention_period = 0
  publicly_accessible     = false
  storage_encrypted       = true
  skip_final_snapshot     = true
}
