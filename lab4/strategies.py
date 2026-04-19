from __future__ import annotations

import csv
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

Record = dict[str, Any]
logger = logging.getLogger(__name__)


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
        if not data:
            logger.info("No records to send to Kafka topic '%s'.", self.topic)
            return

        producer = None
        try:
            from kafka import KafkaProducer

            producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
                request_timeout_ms=5000,
                api_version_auto_timeout_ms=5000,
            )

            if not producer.bootstrap_connected():
                raise ConnectionError(
                    f"Unable to connect to Kafka bootstrap servers: {self.bootstrap_servers}"
                )

            logger.info(
                "Kafka connection established. Sending %d record(s) to topic '%s'.",
                len(data),
                self.topic,
            )

            futures = []
            for row in data:
                futures.append(producer.send(self.topic, row))

            for future in futures:
                future.get(timeout=10)

            producer.flush(timeout=10)
            logger.info("Sent %d record(s) to Kafka topic '%s'.", len(data), self.topic)
        except Exception as exc:
            if not self.simulate_on_error:
                logger.exception("Kafka output failed and simulation mode is disabled.")
                raise
            self._simulate_send(data, exc)
        finally:
            if producer is not None:
                producer.close()

    def _simulate_send(self, data: list[Record], exc: Exception) -> None:
        logger.warning("Kafka not available (%s). Running in simulation mode.", exc)
        for index, row in enumerate(data[:3], start=1):
            logger.info(
                "[Kafka simulation] topic=%s, record=%d: %s",
                self.topic,
                index,
                json.dumps(row, ensure_ascii=False),
            )
        logger.info(
            "Simulated sending %d record(s) to Kafka topic '%s'.",
            len(data),
            self.topic,
        )


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
        if not data:
            logger.info(
                "No records to write to Redis with key prefix '%s'.",
                self.key_prefix,
            )
            return

        client = None
        try:
            import redis

            client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
            )

            if not client.ping():
                raise ConnectionError(f"Redis ping failed for {self.host}:{self.port}/{self.db}")

            pipeline = client.pipeline(transaction=False)
            for index, row in enumerate(data, start=1):
                key = f"{self.key_prefix}:{index}"
                pipeline.set(key, json.dumps(row))

            pipeline.execute()
            logger.info(
                "Stored %d record(s) in Redis with key prefix '%s:*'.",
                len(data),
                self.key_prefix,
            )
        except Exception as exc:
            if not self.simulate_on_error:
                logger.exception("Redis output failed and simulation mode is disabled.")
                raise
            self._simulate_write(data, exc)
        finally:
            if client is not None:
                client.close()

    def _simulate_write(self, data: list[Record], exc: Exception) -> None:
        logger.warning("Redis not available (%s). Running in simulation mode.", exc)
        for index, row in enumerate(data[:3], start=1):
            key = f"{self.key_prefix}:{index}"
            logger.info("[Redis simulation] key=%s, value=%s", key, json.dumps(row))
        logger.info("Simulated saving %d record(s) to Redis.", len(data))


class FirebaseOutputStrategy(OutputStrategy):
    """Concrete Strategy: save rows to Firebase Realtime Database or simulate."""

    def __init__(
        self,
        credentials_path: str,
        database_url: str,
        node_path: str = "/kpi_data",
        simulate_on_error: bool = True,
        app_name: str = "lab4-firebase",
    ) -> None:
        self.credentials_path = Path(credentials_path)
        self.database_url = database_url.strip()
        self.node_path = node_path if node_path.startswith("/") else f"/{node_path}"
        self.simulate_on_error = simulate_on_error
        self.app_name = app_name

    def write(self, data: list[Record]) -> None:
        if not data:
            logger.info("No records to write to Firebase node '%s'.", self.node_path)
            return

        try:
            self._write_to_firebase(data)
            logger.info(
                "Stored %d record(s) in Firebase Realtime Database node '%s'.",
                len(data),
                self.node_path,
            )
        except Exception as exc:
            if not self.simulate_on_error:
                logger.exception("Firebase output failed and simulation mode is disabled.")
                raise
            self._simulate_write(data, exc)

    def _write_to_firebase(self, data: list[Record]) -> None:
        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"Firebase credentials file not found: {self.credentials_path}"
            )
        if not self.database_url:
            raise ValueError("firebase.database_url is required.")

        import firebase_admin
        from firebase_admin import credentials, db

        app = self._get_or_create_app(firebase_admin, credentials)
        db.reference(self.node_path, app=app).set(data)

    def _get_or_create_app(
        self,
        firebase_admin_module: Any,
        credentials_module: Any,
    ) -> Any:
        try:
            return firebase_admin_module.get_app(self.app_name)
        except ValueError:
            certificate = credentials_module.Certificate(str(self.credentials_path))
            return firebase_admin_module.initialize_app(
                certificate,
                {"databaseURL": self.database_url},
                name=self.app_name,
            )

    def _simulate_write(self, data: list[Record], exc: Exception) -> None:
        logger.warning("Firebase not available (%s). Running in simulation mode.", exc)
        for index, row in enumerate(data[:3], start=1):
            logger.info(
                "[Firebase simulation] node=%s, record=%d: %s",
                self.node_path,
                index,
                json.dumps(row, ensure_ascii=False),
            )
        logger.info(
            "Simulated writing %d record(s) to Firebase node '%s'.",
            len(data),
            self.node_path,
        )
