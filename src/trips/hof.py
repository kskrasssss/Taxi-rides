from __future__ import annotations

import operator                                  # звідси беремо ge, eq і т.д. за іменем рядка
from functools import partial, reduce
from typing import Any, Callable

Rec = dict[str, Any]
Func = Callable[[Any], Any]   # тип "функція від одного аргумента до чогось"


def identity(x: Any) -> Any:
    # функція "нічого не робить" — потрібна як стартове значення для compose (щоб reduce мав з чого починати)
    return x


def compose2(f: Func, g: Func) -> Func:
    # бере дві функції й повертає ОДНУ нову: x -> f(g(x))
    def composed(x: Any) -> Any:
        return f(g(x))
    return composed


def compose(*funcs: Func) -> Func:
    # згортає список функцій попарно через compose2, зліва направо за списком,
    # але результат виконується СПРАВА НАЛІВО: compose(f, g, h)(x) == f(g(h(x)))
    return reduce(compose2, funcs, identity)


def pipe(*funcs: Func) -> Func:
    # той самий compose, але з розвернутим порядком аргументів -> виконання ЗЛІВА НАПРАВО
    # pipe(f, g, h)(x) == h(g(f(x)))
    return compose(*reversed(funcs))


def strip_strings(rec: Rec) -> Rec:
    # елементарне перетворення №1 нормалізації: прибрати пробіли з усіх рядкових полів
    return {k: v.strip() if isinstance(v, str) else v for k, v in rec.items()}


def lower_category(rec: Rec) -> Rec:
    # елементарне перетворення №2: категорійне поле (from_zone) до нижнього регістру
    return {**rec, "from_zone": rec["from_zone"].lower()}


def to_int_number(rec: Rec) -> Rec:
    # елементарне перетворення №3: числові поля рядок -> int
    return {**rec, "km": int(rec["km"]), "minutes": int(rec["minutes"])}


# список функцій ЯК ДАНІ (завд. 3.2) — можна зберігати в змінній, перебирати циклом, передавати кудись
TRANSFORMS: tuple[Func, ...] = (strip_strings, lower_category, to_int_number)

# normalize зібраний як КОМПОЗИЦІЯ через pipe — саме тому в pipeline.py імпортують "normalize" звідси, а не пишуть заново
normalize: Callable[[Rec], Rec] = pipe(*TRANSFORMS)


def normalize_loop(rec: Rec) -> Rec:
    # той самий результат, що й normalize вище, але звичайним циклом по списку — доводить,
    # що compose/pipe не роблять нічого магічного, це те саме, що ручний цикл
    for transform in TRANSFORMS:
        rec = transform(rec)
    return rec


def make_predicate(field: str, op: str, value: Any) -> Callable[[Rec], bool]:
    # ФАБРИКА замикань: повертає НОВУ функцію, яка "пам'ятає" field, op, value навіть після завершення make_predicate
    compare = getattr(operator, op)   # рядок "ge" -> сама функція operator.ge

    def predicate(rec: Rec) -> bool:
        return compare(rec[field], value)   # замикання: читає field/op/value із зовнішньої функції
    return predicate


def make_running_total() -> Callable[[float], float]:
    # ФАБРИКА замикання зі ЗМІННИМ станом (на відміну від make_predicate, де стан лише читається)
    total = 0

    def add(x: float) -> float:
        nonlocal total   # без цього total += x створило б НОВУ локальну змінну total всередині add — помилка
        total += x
        return total
    return add   # кожен виклик make_running_total() створює СВІЙ окремий "total", вони не перетинаються


# лямбда з тернарним виразом (завд. 3.4): у lambda можна писати лише ВИРАЗ, а тернарний "if-else" це вираз, не оператор
classify_km = lambda km: "мало" if km < 5 else "звичайно" if km < 20 else "багато"  # noqa: E731


def scale(factor: float, value: float) -> float:
    # звичайна функція двох аргументів — база для часткового застосування нижче
    return round(value * factor, 2)


# partial фіксує ПЕРШИЙ аргумент (factor) одразу, лишає другий (value) — так з'являються "спеціалізовані" функції
to_km = partial(scale, 1.609344)      # милі -> км
to_miles = partial(scale, 0.621371)   # км -> милі

# partial можна застосувати й до власної функції: фіксуємо перші ДВА аргументи (field, op),
# лишається задати тільки value (поріг), щоб отримати готовий предикат
km_predicate = partial(make_predicate, "km", "ge")


def curry3(f: Callable[..., Any]) -> Callable[[Any], Callable[[Any], Callable[[Any], Any]]]:
    # каррирування: перетворює f(a, b, c) на f(a)(b)(c) — три вкладені функції, кожна чекає ОДИН аргумент
    def step1(a: Any) -> Callable[[Any], Callable[[Any], Any]]:
        def step2(b: Any) -> Callable[[Any], Any]:
            def step3(c: Any) -> Any:
                return f(a, b, c)   # тут "спрацьовує" замикання: a, b, c зібрані з трьох різних викликів
            return step3
        return step2
    return step1