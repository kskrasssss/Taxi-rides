from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


@dataclass(frozen=True, slots=True)
class Record:
    from_zone: str
    to_zone: str
    km: int
    minutes: int
    received_at: float


def to_record(d: dict[str, Any]) -> Record:
    return Record(
        from_zone=d["from_zone"],
        to_zone=d["to_zone"],
        km=d["km"],
        minutes=d["minutes"],
        received_at=d["received_at"],
    )


def add_km(rec: Record, delta: int) -> Record:
    """Новий запис зі зміненим числовим полем."""
    return replace(rec, km=rec.km + delta)


def with_to_zone(rec: Record, zone: str) -> Record:
    """Новий запис зі зміненим рядковим полем."""
    return replace(rec, to_zone=zone)