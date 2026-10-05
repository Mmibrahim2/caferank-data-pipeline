from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import requests


def extract_csv(*, url: str | None, file: Path | None, timeout: int = 30) -> tuple[bytes, pd.DataFrame]:
    """Fetch CSV bytes and parse them. A local file makes development deterministic."""
    if url:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        raw = response.content
    elif file:
        raw = file.read_bytes()
    else:
        raise ValueError("Set SOURCE_URL or SOURCE_FILE")

    return raw, pd.read_csv(BytesIO(raw))

