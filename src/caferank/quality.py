from __future__ import annotations

import pandas as pd


def validate(cafes: pd.DataFrame, ranks: pd.DataFrame) -> None:
    """Fail the run before publishing invalid curated data."""
    errors: list[str] = []
    if cafes.empty:
        errors.append("no active cafes found")
    if cafes["cafe_id"].duplicated().any():
        errors.append("cafe_id is not unique")
    if cafes[["cafe_id", "business_name", "neighborhood"]].isna().any().any():
        errors.append("critical cafe fields contain nulls")
    if not cafes["latitude"].dropna().between(44.7, 45.3).all():
        errors.append("latitude outside Minneapolis bounds")
    if not cafes["longitude"].dropna().between(-93.6, -93.0).all():
        errors.append("longitude outside Minneapolis bounds")
    if int(ranks["cafe_count"].sum()) != len(cafes):
        errors.append("ranking counts do not reconcile with cafes")
    if errors:
        raise ValueError("Data quality failed: " + "; ".join(errors))

