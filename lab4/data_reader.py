from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from strategies import OutputStrategy

Record = dict[str, Any]


class DataReader:
    """Context class in Strategy pattern.

    This class has a single responsibility: read input data and delegate output
    behavior to the injected strategy object.
    """

    def __init__(self, output_strategy: OutputStrategy) -> None:
        # Dependency Injection: context receives the strategy from outside.
        self._output_strategy = output_strategy

    def set_output_strategy(self, output_strategy: OutputStrategy) -> None:
        self._output_strategy = output_strategy

    def read_csv(self, csv_path: Path) -> list[Record]:
        if not csv_path.exists():
            raise FileNotFoundError(f"Input CSV was not found: {csv_path}")

        with csv_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            return [dict(row) for row in reader]

    def process(self, csv_path: Path) -> None:
        data = self.read_csv(csv_path)
        self._output_strategy.write(data)
