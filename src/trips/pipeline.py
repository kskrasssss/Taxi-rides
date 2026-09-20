from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
from functools import reduce
from typing import Callable
from .hof import make_predicate, normalize   # вже є normalize; додай make_predicate
from collections import Counter

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


@dataclass(frozen=True)
class Result:
    records: tuple[Rec, ...]
    errors: int


def process(lines: Iterable[str], now: float) -> Result:
    """Чиста функція: нічого не відкриває, не друкує, не читає час."""
    parsed = [parse(line) for line in lines]
    good = tuple({**rec, "received_at": now} for rec in parsed if rec is not None)
    return Result(records=good, errors=sum(rec is None for rec in parsed))



def normalize_plain(rec: Rec) -> Rec:
    return {
        **rec,
        "from_zone": rec["from_zone"].strip().lower(),
        "to_zone": rec["to_zone"].strip(),
        "km": int(rec["km"]),
        "minutes": int(rec["minutes"]),
    }

THRESHOLD = 5

keep: Callable[[Rec], bool] = make_predicate("km", "ge", THRESHOLD)


def add_to_groups(acc: dict[str, int], rec: Rec) -> dict[str, int]:
    """Чиста версія: повертає новий словник, acc не мутує."""
    key = rec["from_zone"]
    return {**acc, key: acc.get(key, 0) + rec["km"]}


def aggregate(records: Iterable[Rec]) -> dict[str, int]:
    return reduce(add_to_groups, records, {})


Predicate = Callable[[Rec], bool]


def run_functional(lines: Iterable[str], keep_fn: Predicate = keep) -> dict[str, int]:
    """Спосіб A: map / filter / reduce."""
    parsed = filter(lambda rec: rec is not None, map(parse, lines))
    normalized = map(normalize, parsed)
    kept = filter(keep_fn, normalized)
    return reduce(add_to_groups, kept, {})


def run_comprehension(lines: Iterable[str], keep_fn: Predicate = keep) -> dict[str, int]:
    """Спосіб B: спискові включення."""
    parsed = [rec for line in lines if (rec := parse(line)) is not None]
    normalized = [normalize(rec) for rec in parsed]
    kept = [rec for rec in normalized if keep_fn(rec)]
    totals: Counter[str] = Counter()
    for rec in kept:
        totals[rec["from_zone"]] += rec["km"]
    return dict(totals)