output "s3_bucket" { value = aws_s3_bucket.data.bucket }
output "github_actions_role_arn" { value = aws_iam_role.pipeline.arn }
output "database_secret_arn" { value = aws_secretsmanager_secret.database_url.arn }
output "database_security_group_id" { value = aws_security_group.database.id }
