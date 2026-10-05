from __future__ import annotations

from io import BytesIO

import boto3
import pandas as pd
from sqlalchemy import create_engine, text


def upload_artifacts(raw: bytes, cafes: pd.DataFrame, ranks: pd.DataFrame, bucket: str, run_date: str, region: str) -> None:
    s3 = boto3.client("s3", region_name=region)
    prefix = f"run_date={run_date}"
    s3.put_object(Bucket=bucket, Key=f"raw/{prefix}/cafes.csv", Body=raw)
    for name, frame in (("cafes", cafes), ("neighborhood_rankings", ranks)):
        buffer = BytesIO()
        frame.to_csv(buffer, index=False)
        s3.put_object(Bucket=bucket, Key=f"curated/{name}/{prefix}/data.csv", Body=buffer.getvalue())


def load_postgres(cafes: pd.DataFrame, ranks: pd.DataFrame, database_url: str) -> None:
    """Load via staging tables, then atomically upsert current entities and daily facts."""
    engine = create_engine(database_url)
    with engine.begin() as connection:
        cafes.to_sql("stg_cafes", connection, if_exists="replace", index=False)
        ranks.to_sql("stg_neighborhood_rankings", connection, if_exists="replace", index=False)
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS cafes (
              cafe_id TEXT PRIMARY KEY, license_id TEXT NOT NULL, business_name TEXT NOT NULL,
              category TEXT, address TEXT, neighborhood TEXT NOT NULL,
              latitude DOUBLE PRECISION, longitude DOUBLE PRECISION, status TEXT, loaded_at TIMESTAMPTZ NOT NULL
            );
            INSERT INTO cafes SELECT cafe_id, license_id, business_name, category, address,
              neighborhood, latitude, longitude, status, loaded_at FROM stg_cafes
            ON CONFLICT (cafe_id) DO UPDATE SET
              business_name=EXCLUDED.business_name, category=EXCLUDED.category,
              address=EXCLUDED.address, neighborhood=EXCLUDED.neighborhood,
              latitude=EXCLUDED.latitude, longitude=EXCLUDED.longitude,
              status=EXCLUDED.status, loaded_at=EXCLUDED.loaded_at;

            CREATE TABLE IF NOT EXISTS neighborhood_rankings (
              neighborhood TEXT NOT NULL, cafe_count INTEGER NOT NULL,
              rank INTEGER NOT NULL, run_date DATE NOT NULL,
              PRIMARY KEY (neighborhood, run_date)
            );
            INSERT INTO neighborhood_rankings SELECT neighborhood, cafe_count, rank, run_date
              FROM stg_neighborhood_rankings
            ON CONFLICT (neighborhood, run_date) DO UPDATE SET
              cafe_count=EXCLUDED.cafe_count, rank=EXCLUDED.rank;
        """))

