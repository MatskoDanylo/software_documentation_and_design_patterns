from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

Record = dict[str, Any]


class OutputStrategy(ABC):
    """Strategy interface: every output target implements the same write API."""

    @abstractmethod
    def write(self, data: list[Record]) -> None:
        """Write parsed KPI rows to a target system."""


class ConsoleOutputStrategy(OutputStrategy):
    """Concrete Strategy: display a preview of rows in the console."""

    def __init__(self, preview_rows: int = 5) -> None:
        self.preview_rows = max(preview_rows, 1)

    def write(self, data: list[Record]) -> None:
        if not data:
            print("No data available to print.")
            return

        preview = data[: self.preview_rows]
        headers = list(preview[0].keys())

        widths: dict[str, int] = {header: len(header) for header in headers}
        for row in preview:
            for header in headers:
                widths[header] = max(widths[header], len(str(row.get(header, ""))))

        header_line = " | ".join(f"{header:<{widths[header]}}" for header in headers)
        separator = "-+-".join("-" * widths[header] for header in headers)

        print(header_line)
        print(separator)
        for row in preview:
            row_line = " | ".join(
                f"{str(row.get(header, '')):<{widths[header]}}" for header in headers
            )
            print(row_line)

        print(f"\nDisplayed {len(preview)} row(s) out of {len(data)} total.")


class FileOutputStrategy(OutputStrategy):
    """Concrete Strategy: save parsed rows into JSON or CSV output files."""

    def __init__(self, output_path: str, file_format: str = "json") -> None:
        self.output_path = Path(output_path)
        self.file_format = file_format.lower().strip()

        if self.file_format not in {"json", "csv"}:
            raise ValueError("file.format must be either 'json' or 'csv'.")

    def write(self, data: list[Record]) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.file_format == "json":
            with self.output_path.open("w", encoding="utf-8") as output_file:
                json.dump(data, output_file, indent=2, ensure_ascii=False)
        else:
            with self.output_path.open("w", newline="", encoding="utf-8") as output_file:
                if data:
                    fieldnames = list(data[0].keys())
                    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)

        print(f"Saved {len(data)} record(s) to '{self.output_path}'.")


class KafkaOutputStrategy(OutputStrategy):
    """Concrete Strategy: send rows to Kafka or simulate when unavailable."""

    def __init__(
        self,
        bootstrap_servers: list[str] | None = None,
        topic: str = "kpi-topic",
        simulate_on_error: bool = True,
    ) -> None:
        self.bootstrap_servers = bootstrap_servers or ["localhost:9092"]
        self.topic = topic
        self.simulate_on_error = simulate_on_error

    def write(self, data: list[Record]) -> None:
        try:
            from kafka import KafkaProducer

            producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            )

            for row in data:
                producer.send(self.topic, row)

            producer.flush()
            producer.close()
            print(f"Sent {len(data)} record(s) to Kafka topic '{self.topic}'.")
        except Exception as exc:
            if not self.simulate_on_error:
                raise
            self._simulate_send(data, exc)

    def _simulate_send(self, data: list[Record], exc: Exception) -> None:
        print(f"Kafka not available ({exc}). Running in simulation mode.")
        for index, row in enumerate(data[:3], start=1):
            print(f"[Kafka simulation] topic={self.topic}, record={index}: {json.dumps(row)}")
        print(f"Simulated sending {len(data)} record(s) to Kafka topic '{self.topic}'.")


class RedisOutputStrategy(OutputStrategy):
    """Concrete Strategy: save rows to Redis keys or simulate when unavailable."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        key_prefix: str = "kpi",
        simulate_on_error: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.db = db
        self.key_prefix = key_prefix
        self.simulate_on_error = simulate_on_error

    def write(self, data: list[Record]) -> None:
        try:
            import redis

            client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
            )

            pipeline = client.pipeline()
            for index, row in enumerate(data, start=1):
                key = f"{self.key_prefix}:{index}"
                pipeline.set(key, json.dumps(row))

            pipeline.execute()
            print(
                f"Stored {len(data)} record(s) in Redis with key prefix "
                f"'{self.key_prefix}:*'."
            )
        except Exception as exc:
            if not self.simulate_on_error:
                raise
            self._simulate_write(data, exc)

    def _simulate_write(self, data: list[Record], exc: Exception) -> None:
        print(f"Redis not available ({exc}). Running in simulation mode.")
        for index, row in enumerate(data[:3], start=1):
            key = f"{self.key_prefix}:{index}"
            print(f"[Redis simulation] key={key}, value={json.dumps(row)}")
        print(f"Simulated saving {len(data)} record(s) to Redis.")
