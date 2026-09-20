from __future__ import annotations

from .pipeline import Predicate, Rec, keep, normalize, parse

from typing import Callable, Iterable, Iterator, TypeVar

T = TypeVar("T")


def g_parse(lines: Iterable[str]) -> Iterator[Rec]:
    for line in lines:
        rec = parse(line)
        if rec is not None:
            yield rec


def g_normalize(records: Iterable[Rec]) -> Iterator[Rec]:
    for rec in records:
        yield normalize(rec)


def g_keep(records: Iterable[Rec], predicate: Predicate = keep) -> Iterator[Rec]:
    for rec in records:
        if predicate(rec):
            yield rec

def record_stream() -> Iterator[Rec]:
    """Нескінченний детермінований потік «сирих» записів."""
    zones = ("Центр", "Оболонь", "Вокзал", "Аеропорт")
    n = 0
    while True:
        zone = zones[n % len(zones)]
        yield {
            "from_zone": f" {zone} " if n % 2 else zone,
            "to_zone": zones[(n + 1) % len(zones)],
            "km": str((n * 7) % 25 + 1),
            "minutes": str(5 + (n * 3) % 40),
        }
        n += 1


def take(n: int, it: Iterable[T]) -> Iterator[T]:
    """Перші n елементів (не тягне зайвого елемента з вхідного ітератора)."""
    if n <= 0:
        return
    for i, x in enumerate(it, 1):
        yield x
        if i >= n:
            return


def drop(n: int, it: Iterable[T]) -> Iterator[T]:
    """Усе, крім перших n елементів."""
    for i, x in enumerate(it):
        if i >= n:
            yield x


def take_while(pred: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    for x in it:
        if not pred(x):
            return
        yield x


def chunked(n: int, it: Iterable[T]) -> Iterator[tuple[T, ...]]:
    buf: list[T] = []
    for x in it:
        buf.append(x)
        if len(buf) == n:
            yield tuple(buf)
            buf = []
    if buf:
        yield tuple(buf)