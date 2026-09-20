from __future__ import annotations

from functools import reduce
from typing import Any, Callable

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