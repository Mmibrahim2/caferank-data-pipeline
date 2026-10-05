output "s3_bucket" { value = aws_s3_bucket.data.bucket }
output "github_actions_role_arn" { value = aws_iam_role.pipeline.arn }

