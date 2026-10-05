from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    source_url: str | None
    source_file: Path | None
    database_url: str | None
    s3_bucket: str | None
    aws_region: str
    run_date: date

    @classmethod
    def from_env(cls) -> Settings:
        raw_date = os.getenv("RUN_DATE")
        return cls(
            source_url=os.getenv("SOURCE_URL") or None,
            source_file=Path(value) if (value := os.getenv("SOURCE_FILE")) else None,
            database_url=os.getenv("DATABASE_URL") or None,
            s3_bucket=os.getenv("S3_BUCKET") or None,
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            run_date=date.fromisoformat(raw_date) if raw_date else datetime.now(timezone.utc).date(),
        )
