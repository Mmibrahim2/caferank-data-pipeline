# CafeRank Data Pipeline

CafeRank is a production-shaped ETL project that extracts Minneapolis café-license data, preserves the raw input in Amazon S3, cleans and ranks it with Pandas, checks data quality, and upserts curated results into PostgreSQL. Terraform provisions the S3 and IAM resources; GitHub Actions tests every change and runs the pipeline daily.

## Architecture

```text
City CSV/API ──extract──> Pandas DataFrame ──transform + validate──┬──> S3 raw/curated
                                                                └──> PostgreSQL
                           GitHub Actions daily schedule
                                      │
                          AWS OIDC short-lived credentials
```

S3 is the immutable, replayable data lake. PostgreSQL is the query-serving layer. Keeping those responsibilities separate lets a failed database load be replayed from S3 without downloading the source again.

## Run locally in five minutes

Prerequisites: Python 3.10+, Docker (only needed for PostgreSQL), and Make.

```bash
python -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
set -a; source .env; set +a
make test
caferank run
```

The checked-in fixture is used by default. To demonstrate PostgreSQL:

```bash
make db-up
export DATABASE_URL='postgresql+psycopg://caferank:caferank@localhost:5432/caferank'
caferank run
docker compose exec postgres psql -U caferank -c 'select * from neighborhood_rankings order by rank;'
```

Unset `DATABASE_URL` for a file-only run. Set `SOURCE_URL` and unset `SOURCE_FILE` to use a real CSV endpoint. Set `S3_BUCKET` after Terraform deployment to enable S3 writes.

## Data model

- `cafes`: one current row per stable license ID. Re-running updates rather than duplicates it.
- `neighborhood_rankings`: one row per neighborhood per run date. This retains ranking history.
- `raw/run_date=YYYY-MM-DD/cafes.csv`: exact source bytes for audit/replay.
- `curated/<dataset>/run_date=YYYY-MM-DD/data.csv`: cleaned outputs for analytics.

The intentionally explainable score is café count per neighborhood. Dense ranking gives tied neighborhoods the same rank and does not create gaps. A future version could add ratings, hours, transit access, or population-normalized density, but calling a simple count a richer “quality score” would be misleading.

## Quality and reliability

The pipeline fails before loading when required columns disappear, IDs duplicate, critical fields are null, coordinates fall outside broad Minneapolis bounds, no cafés remain, or aggregate counts do not reconcile. PostgreSQL writes run in one transaction and use conflict-aware upserts, so retries are idempotent. Date-partitioned S3 keys retain lineage.

Run `make test` and `make lint`. Tests use a small deterministic fixture, not a changing network service.

## Deploy

1. Create a PostgreSQL database (RDS is suitable) and put its SQLAlchemy connection URL in AWS Secrets Manager as the secret value.
2. Ensure the AWS account has GitHub's OIDC provider configured once.
3. Copy `terraform/terraform.tfvars.example` to `terraform/terraform.tfvars`, then run `terraform init`, `terraform plan`, and `terraform apply` inside `terraform/`.
4. Add the Terraform output values as GitHub environment secret `AWS_ROLE_ARN` and variable `S3_BUCKET`. Add `DB_SECRET_ARN` as a secret; add `AWS_REGION` and `SOURCE_URL` as variables.
5. Trigger the workflow manually, then inspect S3 and query PostgreSQL.

Terraform intentionally does not create RDS in this portfolio baseline because a continuously running database costs money. The interface supports local PostgreSQL or an existing RDS instance; provisioning RDS is a clear extension.

## Repository map

```text
src/caferank/       ETL application
tests/              unit and data-quality tests
data/               deterministic demo input
terraform/          S3 and least-privilege GitHub OIDC role
.github/workflows/  CI and daily orchestration
INTERVIEW_GUIDE.md  design explanation and likely questions
```

## Source note

Minneapolis is migrating its open-data experience, so the source URL is configuration rather than code. Obtain a current CSV/export URL from the city's OpenDataMPLS/MinneapolisData catalog and map its columns to the canonical input schema if they differ. The canonical columns are `license_id`, `business_name`, `category`, `address`, `neighborhood`, `latitude`, `longitude`, and `status`.
