from __future__ import annotations

import re
from datetime import date

import pandas as pd

REQUIRED_COLUMNS = {
    "license_id",
    "business_name",
    "category",
    "address",
    "neighborhood",
    "latitude",
    "longitude",
    "status",
}


def _slug(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).strip().lower()).strip("-")


def transform(raw: pd.DataFrame, run_date: date) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Normalize active cafe-like licenses and calculate transparent neighborhood ranks."""
    missing = REQUIRED_COLUMNS - set(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    cafes = raw.copy()
    cafes.columns = cafes.columns.str.strip().str.lower()
    for column in ["license_id", "business_name", "category", "address", "neighborhood", "status"]:
        cafes[column] = cafes[column].astype("string").str.strip()

    cafes["latitude"] = pd.to_numeric(cafes["latitude"], errors="coerce")
    cafes["longitude"] = pd.to_numeric(cafes["longitude"], errors="coerce")
    cafe_pattern = r"coffee|cafe|espresso|roast"
    cafes = cafes[
        cafes["category"].str.contains(cafe_pattern, case=False, na=False)
        & cafes["status"].str.casefold().eq("active")
    ].copy()
    cafes = cafes.dropna(subset=["license_id", "business_name", "neighborhood"])
    cafes = cafes.drop_duplicates(subset=["license_id"], keep="last")
    cafes["cafe_id"] = cafes["license_id"].map(_slug)
    cafes["loaded_at"] = pd.Timestamp(run_date, tz="UTC")

    ranks = (
        cafes.groupby("neighborhood", as_index=False)
        .agg(cafe_count=("cafe_id", "nunique"))
        .sort_values(["cafe_count", "neighborhood"], ascending=[False, True])
    )
    ranks["rank"] = ranks["cafe_count"].rank(method="dense", ascending=False).astype(int)
    ranks["run_date"] = run_date
    return cafes.reset_index(drop=True), ranks.reset_index(drop=True)
