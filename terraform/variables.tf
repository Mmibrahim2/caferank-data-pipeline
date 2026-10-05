variable "aws_region" { type = string; default = "us-east-1" }
variable "project_name" { type = string; default = "caferank" }
variable "github_repository" {
  description = "GitHub owner/repository allowed to assume the pipeline role"
  type = string
}
variable "database_url_secret_arn" {
  description = "ARN of an existing Secrets Manager secret containing DATABASE_URL"
  type = string
}

