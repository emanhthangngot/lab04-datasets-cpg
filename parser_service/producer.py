"""Kafka producer helpers."""

from __future__ import annotations

import json

try:
    from kafka import KafkaProducer
except ImportError:  # pragma: no cover - allows scaffold tests without Kafka deps installed
    KafkaProducer = None


class DryRunProducer:
    """Producer used for local scaffold checks without Kafka."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, str, dict]] = []
        self.flush_count = 0

    def send(self, topic: str, key: str, value: dict) -> None:
        self.messages.append((topic, key, value))

    def flush(self, timeout: int | None = None) -> None:
        self.flush_count += 1

    def close(self, timeout: int | None = None) -> None:
        return None


def build_producer(bootstrap_servers: str, dry_run: bool = False):
    """Build a Kafka producer or dry-run producer.

    TODO: In final runtime, prefer real Kafka producer and capture sample
    messages in notebook 03.
    """

    if dry_run:
        return DryRunProducer()
    if KafkaProducer is None:
        raise RuntimeError("kafka-python is not installed. Run pip install -r requirements.txt.")
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",
        retries=3,
        linger_ms=10,
    )
