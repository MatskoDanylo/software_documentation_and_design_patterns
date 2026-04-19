from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from data_reader import DataReader
from strategies import (
    ConsoleOutputStrategy,
    FileOutputStrategy,
    FirebaseOutputStrategy,
    KafkaOutputStrategy,
    OutputStrategy,
    RedisOutputStrategy,
)


def load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def resolve_path(base_dir: Path, path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = base_dir / path
    return path


def build_output_strategy(config: dict[str, Any], base_dir: Path) -> OutputStrategy:
    # Factory Method: chooses concrete strategy based only on configuration.
    output_type = str(config.get("output_type", "console")).lower()

    if output_type == "console":
        console_cfg = config.get("console", {})
        return ConsoleOutputStrategy(preview_rows=int(console_cfg.get("preview_rows", 5)))

    if output_type == "file":
        file_cfg = config.get("file", {})
        output_path = resolve_path(
            base_dir,
            str(file_cfg.get("output_path", "output/kpi_data.json")),
        )
        return FileOutputStrategy(
            output_path=str(output_path),
            file_format=str(file_cfg.get("format", "json")),
        )

    if output_type == "kafka":
        kafka_cfg = config.get("kafka", {})
        bootstrap_servers = kafka_cfg.get("bootstrap_servers", ["localhost:9092"])
        if isinstance(bootstrap_servers, str):
            bootstrap_servers = [bootstrap_servers]

        return KafkaOutputStrategy(
            bootstrap_servers=list(bootstrap_servers),
            topic=str(kafka_cfg.get("topic", "kpi-topic")),
            simulate_on_error=bool(kafka_cfg.get("simulate_on_error", True)),
        )

    if output_type == "redis":
        redis_cfg = config.get("redis", {})
        return RedisOutputStrategy(
            host=str(redis_cfg.get("host", "localhost")),
            port=int(redis_cfg.get("port", 6379)),
            db=int(redis_cfg.get("db", 0)),
            key_prefix=str(redis_cfg.get("key_prefix", "kpi")),
            simulate_on_error=bool(redis_cfg.get("simulate_on_error", True)),
        )

    if output_type == "firebase":
        firebase_cfg = config.get("firebase", {})
        credentials_path = resolve_path(
            base_dir,
            str(firebase_cfg.get("credentials_path", "firebase-key.json")),
        )
        return FirebaseOutputStrategy(
            credentials_path=str(credentials_path),
            database_url=str(firebase_cfg.get("database_url", "")),
            node_path=str(firebase_cfg.get("node_path", "/kpi_data")),
            simulate_on_error=bool(firebase_cfg.get("simulate_on_error", True)),
        )

    supported_types = "console, file, kafka, redis, firebase"
    raise ValueError(
        f"Unsupported output_type '{output_type}'. "
        f"Supported values: {supported_types}"
    )


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "config.json"
    config = load_config(config_path)

    input_csv_path = resolve_path(base_dir, str(config.get("input_csv", "kpi-prifsma.csv")))

    strategy = build_output_strategy(config, base_dir)

    # Context uses injected strategy; no source-code changes required for switching.
    reader = DataReader(strategy)
    reader.process(input_csv_path)


if __name__ == "__main__":
    main()
