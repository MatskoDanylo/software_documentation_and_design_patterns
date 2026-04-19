from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .interfaces import ICSVReader


class FlatCSVReader(ICSVReader):
    """Concrete CSV reader for flat onboarding records."""

    def __init__(self, csv_path: str) -> None:
        self._csv_path = Path(csv_path)

    def read_rows(self) -> Iterable[dict[str, str]]:
        with self._csv_path.open(mode="r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                yield {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}

