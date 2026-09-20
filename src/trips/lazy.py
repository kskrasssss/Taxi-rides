from __future__ import annotations

from typing import Iterable, Iterator

from .pipeline import Predicate, Rec, keep, normalize, parse


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