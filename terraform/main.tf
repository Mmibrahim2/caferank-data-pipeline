data "aws_caller_identity" "current" {}

resource "random_id" "suffix" { byte_length = 4 }

resource "aws_s3_bucket" "data" {
  bucket = "${var.project_name}-${data.aws_caller_identity.current.account_id}-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    id = "archive-raw"
    status = "Enabled"
    filter {
      prefix = "raw/"
    }
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
  }
}

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

data "aws_iam_policy_document" "github_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values = ["sts.amazonaws.com"]
    }
    condition {
      test = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = ["repo:${var.github_repository}:*"]
    }
  }
}

resource "aws_iam_role" "pipeline" {
  name = "${var.project_name}-github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_assume.json
}

data "aws_iam_policy_document" "pipeline" {
  statement {
    actions = ["s3:ListBucket"]
    resources = [aws_s3_bucket.data.arn]
  }
  statement {
    actions = ["s3:PutObject", "s3:GetObject"]
    resources = ["${aws_s3_bucket.data.arn}/*"]
  }
  statement {
    actions = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.database_url.arn]
  }
  statement {
    actions = ["ec2:AuthorizeSecurityGroupIngress", "ec2:RevokeSecurityGroupIngress"]
    resources = ["*"]
    condition {
      test = "StringEquals"
      variable = "aws:ResourceTag/Project"
      values = [var.project_name]
    }
  }
}

resource "aws_iam_role_policy" "pipeline" {
  role = aws_iam_role.pipeline.id
  policy = data.aws_iam_policy_document.pipeline.json
}

data "aws_vpc" "default" { default = true }
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_db_subnet_group" "main" {
  name = "${var.project_name}-default"
  subnet_ids = data.aws_subnets.default.ids
  tags = { Project = var.project_name }
}

resource "aws_security_group" "database" {
  name = "${var.project_name}-postgres"
  description = "Temporary GitHub runner access to CafeRank PostgreSQL"
  vpc_id = data.aws_vpc.default.id
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Project = var.project_name }
}

resource "random_password" "database" {
  length = 32
  special = false
}

resource "aws_db_instance" "postgres" {
  identifier = "${var.project_name}-postgres"
  engine = "postgres"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  storage_type = "gp2"
  db_name = var.db_name
  username = var.db_username
  password = random_password.database.result
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.database.id]
  publicly_accessible = true
  multi_az = false
  storage_encrypted = true
  backup_retention_period = 1
  skip_final_snapshot = true
  deletion_protection = false
  apply_immediately = true
  tags = { Project = var.project_name }
}

resource "aws_secretsmanager_secret" "database_url" {
  name = "${var.project_name}/database-url"
  recovery_window_in_days = 7
  tags = { Project = var.project_name }
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id = aws_secretsmanager_secret.database_url.id
  secret_string = "postgresql+psycopg://${var.db_username}:${random_password.database.result}@${aws_db_instance.postgres.address}:${aws_db_instance.postgres.port}/${var.db_name}?sslmode=require"
}
