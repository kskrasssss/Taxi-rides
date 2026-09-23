from __future__ import annotations

import math
from dataclasses import dataclass

# Кожен вид вузла виразу — окремий frozen dataclass.
# dataclass автоматично генерує __match_args__ = ("a", "b") і т.д., САМЕ ТОМУ нижче в evaluate
# працює позиційний патерн "case Add(a, b)" — Python знає, яке поле відповідає якій позиції.


@dataclass(frozen=True)
class Num:
    value: float   # число


@dataclass(frozen=True)
class Neg:
    x: "Expr"   # унарний мінус; рядок "Expr" — бо Expr оголошений нижче за файлом


@dataclass(frozen=True)
class Add:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Sub:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Mul:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Div:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Pow:
    base: "Expr"
    exp: int   # звичайне ціле число, НЕ піддерево — тому в evaluate exp порівнюють напряму, без рекурсії


@dataclass(frozen=True)
class Sqrt:
    x: "Expr"


@dataclass(frozen=True)
class Sum:
    terms: tuple["Expr", ...]   # довільна кількість доданків


# Expr — це "тип-об'єднання": будь-який з перелічених класів. Використовується лише для анотацій.
Expr = Num | Neg | Add | Sub | Mul | Div | Pow | Sqrt | Sum


def evaluate(node: Expr) -> float:
    # ПОРЯДОК гілок важливий: конкретніші випадки мають стояти ПЕРЕД загальнішими
    match node:
        case Num(0):
            # ЛІТЕРАЛЬНИЙ патерн: спрацює тільки для Num З ТОЧНИМ значенням поля 0
            return 0.0
        case Num(v):
            # загальний випадок Num — мусить стояти ПІСЛЯ Num(0), інакше той ніколи не спрацює
            return float(v)
        case Neg(x):
            # ПАТЕРН КЛАСУ з деконструкцією: одразу перевіряє тип І дістає поле x в змінну
            return -evaluate(x)   # рекурсивний виклик evaluate на піддереві
        case Add(a, b):
            return evaluate(a) + evaluate(b)
        case Sub(a, b):
            return evaluate(a) - evaluate(b)
        case Mul(a, b):
            return evaluate(a) * evaluate(b)
        case Div(a, b):
            divisor = evaluate(b)
            if divisor == 0:
                raise ValueError("ділення на нуль")
            return evaluate(a) / divisor
        case Pow(base, exp) if exp >= 0:
            # GUARD-умова: патерн Pow(base, exp) спрацьовує лише якщо ще й exp >= 0
            return evaluate(base) ** exp
        case Pow():
            # сюди потрапляє Pow, що НЕ пройшов guard вище (тобто exp < 0) — мусить стояти ПІСЛЯ гілки з guard
            raise ValueError("від'ємний показник")
        case Sqrt(x):
            value = evaluate(x)
            if value < 0:
                raise ValueError("корінь із від'ємного числа")
            return math.sqrt(value)
        case Sum(()):
            # порожній кортеж доданків — база рекурсії для Sum
            return 0.0
        case Sum((first, *rest)):
            # РОЗПАКУВАННЯ послідовності: перший елемент окремо, "хвіст" (*rest) — знову як кортеж
            # рекурсивний крок: перший доданок + сума решти (обгорнутої назад у Sum)
            return evaluate(first) + evaluate(Sum(tuple(rest)))
        case _:
            # символ _ — "все інше", ловить значення, що не є жодним відомим вузлом (наприклад, просто число 42)
            raise ValueError(f"невідомий вузол: {node!r}")