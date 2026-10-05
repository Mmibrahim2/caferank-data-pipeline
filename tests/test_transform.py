from datetime import date

import pandas as pd
import pytest

from caferank.quality import validate
from caferank.transform import transform


def source_frame() -> pd.DataFrame:
    return pd.DataFrame([
        {"license_id": "1", "business_name": "A", "category": "Coffee Shop", "address": "1 Main", "neighborhood": "North", "latitude": 44.98, "longitude": -93.27, "status": "Active"},
        {"license_id": "2", "business_name": "B", "category": "Cafe", "address": "2 Main", "neighborhood": "North", "latitude": 44.99, "longitude": -93.26, "status": "Active"},
        {"license_id": "3", "business_name": "C", "category": "Restaurant", "address": "3 Main", "neighborhood": "South", "latitude": 44.95, "longitude": -93.28, "status": "Active"},
        {"license_id": "4", "business_name": "D", "category": "Cafe", "address": "4 Main", "neighborhood": "South", "latitude": 44.94, "longitude": -93.29, "status": "Inactive"},
    ])


def test_transform_filters_and_ranks() -> None:
    cafes, ranks = transform(source_frame(), date(2026, 1, 2))
    assert cafes["business_name"].tolist() == ["A", "B"]
    assert ranks.to_dict("records") == [{"neighborhood": "North", "cafe_count": 2, "rank": 1, "run_date": date(2026, 1, 2)}]
    validate(cafes, ranks)


def test_missing_schema_fails() -> None:
    with pytest.raises(ValueError, match="Missing required columns"):
        transform(source_frame().drop(columns="license_id"), date(2026, 1, 2))


def test_quality_rejects_bad_coordinates() -> None:
    cafes, ranks = transform(source_frame(), date(2026, 1, 2))
    cafes.loc[0, "latitude"] = 10
    with pytest.raises(ValueError, match="latitude"):
        validate(cafes, ranks)
