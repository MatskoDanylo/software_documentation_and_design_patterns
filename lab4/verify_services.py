from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("verify_services")


def load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def verify_redis(redis_config: dict[str, Any]) -> bool:
    try:
        import redis

        host = str(redis_config.get("host", "localhost"))
        port = int(redis_config.get("port", 6379))
        db = int(redis_config.get("db", 0))

        client = redis.Redis(
            host=host,
            port=port,
            db=db,
            socket_connect_timeout=3,
            socket_timeout=3,
            decode_responses=True,
        )
        ping_result = client.ping()
        client.close()

        if ping_result:
            logger.info("Redis reachable at %s:%d/%d.", host, port, db)
            return True

        logger.error("Redis ping returned an unexpected result.")
        return False
    except Exception as exc:
        logger.error("Redis verification failed: %s", exc)
        return False


def verify_kafka(kafka_config: dict[str, Any]) -> bool:
    try:
        from kafka import KafkaAdminClient

        bootstrap_servers = kafka_config.get("bootstrap_servers", ["localhost:9092"])
        if isinstance(bootstrap_servers, str):
            bootstrap_servers = [bootstrap_servers]

        admin_client = KafkaAdminClient(
            bootstrap_servers=list(bootstrap_servers),
            request_timeout_ms=5000,
            api_version_auto_timeout_ms=5000,
        )
        topics = admin_client.list_topics()
        admin_client.close()

        logger.info(
            "Kafka reachable at %s. Topic count discovered: %d.",
            list(bootstrap_servers),
            len(topics),
        )
        return True
    except Exception as exc:
        logger.error("Kafka verification failed: %s", exc)
        return False


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    config = load_config(base_dir / "config.json")

    kafka_ok = verify_kafka(config.get("kafka", {}))
    redis_ok = verify_redis(config.get("redis", {}))

    if kafka_ok and redis_ok:
        logger.info("All external services are reachable.")
        return 0

    logger.error("One or more services are not reachable. Check Docker containers and ports.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
