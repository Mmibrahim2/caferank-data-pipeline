# CafeRank interview guide

## 30-second pitch

“CafeRank is a daily batch ETL pipeline for Minneapolis café-license data. Python downloads a CSV, Pandas normalizes and filters active café-like businesses, validates the result, and ranks neighborhoods by café count. It stores immutable raw and partitioned curated files in S3, then transactionally upserts serving tables in PostgreSQL. Terraform manages AWS storage and least-privilege GitHub OIDC access, while GitHub Actions runs tests on every change and schedules production daily.”

## Walk through one run

1. `Settings.from_env()` separates configuration from code and makes the same artifact portable.
2. Extract returns both exact bytes for lineage and a DataFrame for processing.
3. Transform checks the contract, normalizes strings/types, filters active café categories, deduplicates stable license IDs, and aggregates neighborhood counts.
4. Quality checks fail fast before any curated destination changes.
5. The loader writes date-partitioned S3 objects and stages PostgreSQL rows.
6. A database transaction creates tables if needed and performs idempotent upserts.
7. The command logs row counts so operators can spot sudden changes.

## Decisions to defend

**Why Pandas?** The dataset is small enough for one machine, and Pandas makes schema cleanup and aggregation concise. At tens of gigabytes or strict low-latency requirements, use Spark/Glue or warehouse-native SQL.

**Why both S3 and PostgreSQL?** S3 cheaply preserves source history and supports replay; PostgreSQL supports indexes, constraints, and interactive SQL for downstream applications.

**Why a daily full snapshot?** Municipal license data changes slowly and is modest in size. Full snapshots reduce incremental-state complexity. If volume grows, use source update timestamps/watermarks and persist checkpoints.

**How is it idempotent?** Café rows use a stable primary key and `ON CONFLICT DO UPDATE`; rankings use `(neighborhood, run_date)`. Re-running a date converges to the same logical result. S3 keys for a run date are deterministic, with bucket versioning preserving overwritten bytes.

**Why GitHub Actions rather than Airflow?** One daily job has no complex DAG, backfills, sensors, or cross-pipeline dependencies. Actions is lower operational overhead. Airflow becomes compelling as dependencies and backfill requirements grow.

**How are secrets protected?** GitHub obtains short-lived AWS credentials through OIDC. The workflow fetches the database URL from Secrets Manager. No long-lived AWS access keys or passwords live in source control.

**What happens on failure?** Requests use a timeout and HTTP errors propagate. Validation stops invalid loads. PostgreSQL changes are transactional. GitHub marks the job failed and retains logs. A mature version would add retry with exponential backoff, alerts, metrics, and a dead-letter/quarantine prefix.

## Be precise about limitations

- A license dataset measures establishments, not customer preference or coffee quality.
- Name/category matching can create false positives or negatives; a maintained category mapping is stronger.
- The broad geographic bounds are a sanity check, not point-in-polygon validation.
- The Terraform baseline expects an existing OIDC provider, database, and secret; it avoids surprise RDS cost.
- Production observability should add structured logs, source/target row-count metrics, duration, and alerts.

## Likely follow-ups

**How would you handle schema drift?** Version the expected contract, quarantine unexpected payloads, alert, and add an explicit mapping/migration rather than silently accepting changed semantics.

**How would you test the loader?** Unit-test S3 calls with a stub, then run PostgreSQL integration tests in a disposable container to verify constraints, transactions, and re-run behavior. Keep network-source tests separate from deterministic CI.

**How would you backfill?** Add `--run-date` and source snapshot selection, then execute dates independently. The partition and primary-key scheme already supports this.

**How would you scale it?** Store Parquet rather than CSV, register a Glue catalog, push transforms to Glue/Spark or a warehouse, use incremental extraction, and orchestrate with Step Functions/Airflow when the workflow becomes a DAG.

## Honest résumé wording

After you deploy and demonstrate it, say:

> Built a tested Python/Pandas ETL pipeline that ingests Minneapolis café-license data, validates and ranks neighborhoods, preserves date-partitioned snapshots in S3, and idempotently upserts PostgreSQL; provisioned encrypted storage and GitHub OIDC IAM with Terraform and scheduled daily runs in GitHub Actions.

Before actual deployment, replace “built” with “developed a local, deployment-ready” so the claim remains accurate.

