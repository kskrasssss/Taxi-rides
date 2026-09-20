from __future__ import annotations

from typing import Any

Rec = dict[str, Any]

FIELDS = ("from_zone", "to_zone", "km", "minutes")


def _is_int(text: str) -> bool:
    try:
        int(text)
    except ValueError:
        return False
    return True


def parse(line: str) -> Rec | None:
    """Розбирає 'from_zone;to_zone;km;minutes'. None — якщо рядок некоректний."""
    parts = line.rstrip("\n").split(";")
    if len(parts) != len(FIELDS):
        return None
    from_zone, to_zone, km, minutes = parts
    if not from_zone.strip() or not to_zone.strip():
        return None
    if not (_is_int(km) and _is_int(minutes)):
        return None
    return dict(zip(FIELDS, parts))  # значення «сирі», нормалізація окремо