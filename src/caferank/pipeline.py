from __future__ import annotations

import logging
from pathlib import Path

from caferank.config import Settings
from caferank.extract import extract_csv
from caferank.load import load_postgres, upload_artifacts
from caferank.quality import validate
from caferank.transform import transform

logger = logging.getLogger(__name__)


def run(settings: Settings, output_dir: Path = Path("data/output")) -> dict[str, int]:
    raw, source = extract_csv(url=settings.source_url, file=settings.source_file)
    cafes, ranks = transform(source, settings.run_date)
    validate(cafes, ranks)

    output_dir.mkdir(parents=True, exist_ok=True)
    cafes.to_csv(output_dir / "cafes.csv", index=False)
    ranks.to_csv(output_dir / "neighborhood_rankings.csv", index=False)

    run_date = settings.run_date.isoformat()
    if settings.s3_bucket:
        upload_artifacts(raw, cafes, ranks, settings.s3_bucket, run_date, settings.aws_region)
    if settings.database_url:
        load_postgres(cafes, ranks, settings.database_url)

    result = {"source_rows": len(source), "cafe_rows": len(cafes), "neighborhood_rows": len(ranks)}
    logger.info("pipeline_complete %s", result)
    return result

