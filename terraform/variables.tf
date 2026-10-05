variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "caferank"
}
variable "github_repository" {
  description = "GitHub owner/repository allowed to assume the pipeline role"
  type = string
}

variable "db_name" {
  type    = string
  default = "caferank"
}

variable "db_username" {
  type    = string
  default = "caferank_admin"
}
