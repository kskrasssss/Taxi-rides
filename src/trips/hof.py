from __future__ import annotations

from functools import reduce
from typing import Any, Callable

import operator

Rec = dict[str, Any]
Func = Callable[[Any], Any]


def identity(x: Any) -> Any:
    return x


def compose2(f: Func, g: Func) -> Func:
    """x -> f(g(x))"""
    def composed(x: Any) -> Any:
        return f(g(x))
    return composed


def compose(*funcs: Func) -> Func:
    """Справа наліво: compose(f, g, h)(x) == f(g(h(x)))."""
    return reduce(compose2, funcs, identity)


def pipe(*funcs: Func) -> Func:
    """Зліва направо: pipe(f, g, h)(x) == h(g(f(x)))."""
    return compose(*reversed(funcs))


def strip_strings(rec: Rec) -> Rec:
    return {k: v.strip() if isinstance(v, str) else v for k, v in rec.items()}


def lower_category(rec: Rec) -> Rec:
    return {**rec, "from_zone": rec["from_zone"].lower()}


def to_int_number(rec: Rec) -> Rec:
    return {**rec, "km": int(rec["km"]), "minutes": int(rec["minutes"])}


# функції як дані: їх можна зберігати в кортежі й перебирати
TRANSFORMS: tuple[Func, ...] = (strip_strings, lower_category, to_int_number)

normalize: Callable[[Rec], Rec] = pipe(*TRANSFORMS)


def normalize_loop(rec: Rec) -> Rec:
    """Той самий результат, але циклом по списку функцій (3.2)."""
    for transform in TRANSFORMS:
        rec = transform(rec)
    return rec


def make_predicate(field: str, op: str, value: Any) -> Callable[[Rec], bool]:
    """Замикає field, op, value; повертає rec -> op(rec[field], value)."""
    compare = getattr(operator, op)

    def predicate(rec: Rec) -> bool:
        return compare(rec[field], value)
    return predicate


def make_running_total() -> Callable[[float], float]:
    total = 0

    def add(x: float) -> float:
        nonlocal total          # змінюємо змінну зовнішньої функції
        total += x
        return total
    return add


# lambda з тернарним виразом (3.4)
classify_km = lambda km: "мало" if km < 5 else "звичайно" if km < 20 else "багато"  # noqa: E731