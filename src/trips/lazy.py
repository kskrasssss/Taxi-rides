from __future__ import annotations

from typing import Callable, Iterable, Iterator, TypeVar

from .pipeline import Predicate, Rec, keep, normalize, parse

T = TypeVar("T")   # узагальнений тип — take/drop/take_while/chunked працюють з БУДЬ-яким типом елементів, не лише Rec


def g_parse(lines: Iterable[str]) -> Iterator[Rec]:
    # ГЕНЕРАТОРНА функція (має yield): не читає всі lines одразу, а видає готові записи по одному, на вимогу
    for line in lines:
        rec = parse(line)
        if rec is not None:
            yield rec   # некоректні рядки просто пропускаються, без None у результаті


def g_normalize(records: Iterable[Rec]) -> Iterator[Rec]:
    # той самий normalize, що й у "жадібних" конвеєрах, але тут він застосовується ЛІНИВО, по одному запису
    for rec in records:
        yield normalize(rec)


def g_keep(records: Iterable[Rec], predicate: Predicate = keep) -> Iterator[Rec]:
    # predicate параметром — можна підставити інший критерій відбору (наприклад, для record_stream нижче)
    for rec in records:
        if predicate(rec):
            yield rec


def record_stream() -> Iterator[Rec]:
    # НЕСКІНЧЕННИЙ генератор: while True без умови виходу. Матеріалізувати його цілком (list(...)) — зависне назавжди
    zones = ("Центр", "Оболонь", "Вокзал", "Аеропорт")
    n = 0
    while True:
        zone = zones[n % len(zones)]
        yield {
            # детермінована формула від лічильника n — тому кожен запуск дає той самий потік
            "from_zone": f" {zone} " if n % 2 else zone,
            "to_zone": zones[(n + 1) % len(zones)],
            "km": str((n * 7) % 25 + 1),
            "minutes": str(5 + (n * 3) % 40),
        }
        n += 1


def take(n: int, it: Iterable[T]) -> Iterator[T]:
    # ВЛАСНИЙ аналог itertools.islice(it, n), без використання itertools
    if n <= 0:
        return   # порожній генератор: return у генераторній функції одразу піднімає StopIteration
    for i, x in enumerate(it, 1):
        yield x
        if i >= n:
            return   # ВАЖЛИВО: виходимо одразу після n-го елемента, НЕ витягуючи (n+1)-й з нескінченного it


def drop(n: int, it: Iterable[T]) -> Iterator[T]:
    # пропускає перші n елементів, решту віддає як є
    for i, x in enumerate(it):
        if i >= n:
            yield x


def take_while(pred: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    # віддає елементи, ПОКИ предикат True; на першому False одразу зупиняється (не перебирає решту)
    for x in it:
        if not pred(x):
            return
        yield x


def chunked(n: int, it: Iterable[T]) -> Iterator[tuple[T, ...]]:
    # ріже послідовність на шматки по n елементів; останній шматок може бути коротшим
    buf: list[T] = []
    for x in it:
        buf.append(x)
        if len(buf) == n:
            yield tuple(buf)
            buf = []
    if buf:            # залишок, менший за n, теж треба віддати
        yield tuple(buf)