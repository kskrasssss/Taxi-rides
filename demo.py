import contextlib
import io
import sys
import time
from pathlib import Path
from typing import Callable

from dataclasses import dataclass
from src.trips.pipeline import normalize_plain, process
from src.trips import legacy
from src.trips.model import Record, add_km, to_record, with_to_zone
from src.trips.hof import normalize

from src.trips.hof import TRANSFORMS, compose, normalize_loop, pipe
from src.trips.pipeline import normalize, normalize_plain, process

from src.trips.hof import classify_km, make_predicate, make_running_total
from src.trips.pipeline import aggregate, keep, normalize, process

from src.trips.pipeline import run_comprehension, run_functional

from src.trips.hof import curry3, km_predicate, make_predicate, to_km, to_miles

from typing import Iterable, Iterator

from src.trips.lazy import g_keep, g_normalize, g_parse
from src.trips.pipeline import aggregate, run_functional
from itertools import islice

from src.trips.lazy import chunked, drop, record_stream, take, take_while

from src.trips.calculator import Add, Div, Mul, Neg, Num, Pow, Sqrt, Sub, Sum, evaluate

sys.path.insert(0, str(Path(__file__).parent / "src"))


DATA = Path(__file__).parent / "data" / "trips.txt"
EXPECTED_ERRORS = 6   # скільки некоректних рядків у data/trips.txt


def section(title: str) -> None:
    print(f"\n{'=' * 8} {title} {'=' * 8}")


def read_lines() -> list[str]:
    return DATA.read_text(encoding="utf-8").splitlines()


def show(label: str, fn: Callable[[], object]) -> None:
    """Виконує fn; друкує результат або перехоплений виняток."""
    try:
        result = fn()
    except Exception as exc:
        print(f"  {label}: {type(exc).__name__}: {exc}")
    else:
        print(f"  {label}: {result!r}")


def demo_task1(lines: list[str]) -> None:
    section("Завдання 1. Чисті функції")
    res1 = process(lines, now=1000.0)
    res2 = process(lines, now=1000.0)
    print("res1 == res2:", res1 == res2)
    print("розібрано:", len(res1.records), "| помилок:", res1.errors,
          "| очікувано:", EXPECTED_ERRORS)
    print("перший запис:", res1.records[0])
    print("з реальним часом:", process(lines, now=time.time()).records[0]["received_at"])

    # для порівняння: «брудна» версія накопичує глобальний стан між викликами
    with contextlib.redirect_stdout(io.StringIO()):   # глушимо її print
        legacy.load(DATA)
        legacy.load(DATA)
    print("legacy після 2 викликів: records =", len(legacy.records),
          "| errors =", legacy.errors, "(стан накопичився!)")
    print("process після 2 викликів: records =", len(res2.records), "(стану немає)")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # щоб кирилиця не ламалась у консолі Windows
    lines = read_lines()          # введення-виведення лишається тут
    demo_task1(lines)

@dataclass                      # без frozen -> eq=True -> __hash__ = None
class MutableRecord:
    from_zone: str
    km: int


def demo_task2(lines: list[str]) -> None:
    section("Завдання 2. Незмінний Record")
    raw = process(lines, now=1000.0).records[0]
    rec = to_record(normalize(raw))
    print("record:", rec)

    show("rec.km = 99", lambda: setattr(rec, "km", 99))   # FrozenInstanceError

    bigger = add_km(rec, 10)
    moved = with_to_zone(rec, "Печерськ")
    print("add_km ->", bigger)
    print("with_to_zone ->", moved)
    print("оригінал не змінився:", rec, "| bigger is rec:", bigger is rec)

    same = to_record(normalize(raw))
    print("set із двох рівних Record, розмір:", len({rec, same}))
    print("Record як ключ dict:", {rec: "поїздка"}[same])
    show("set з MutableRecord", lambda: {MutableRecord("центр", 5)})   # TypeError

def demo_task3(lines: list[str]) -> None:
    section("Завдання 3. Функції вищого порядку")
    print("-- compose / pipe --")
    f = lambda x: x + 1
    g = lambda x: x * 2
    h = lambda x: x - 3
    print("compose(f,g,h)(10):", compose(f, g, h)(10), "| f(g(h(10))):", f(g(h(10))))
    print("pipe(f,g,h)(10):   ", pipe(f, g, h)(10), "| h(g(f(10))):", h(g(f(10))))

    print("-- normalize --")
    raw = process(lines, now=1000.0).records
    print("pipe == loop == plain для всіх записів:",
          all(normalize(r) == normalize_loop(r) == normalize_plain(r) for r in raw))
    print("кількість перетворень у списку:", len(TRANSFORMS))
    print("приклад:", normalize(raw[0]))

def demo_task3_closures(lines: list[str]) -> None:
    print("\n-- замикання --")
    records = [normalize(r) for r in process(lines, now=1000.0).records]

    ge5 = make_predicate("km", "ge", 5)
    is_center = make_predicate("from_zone", "eq", "центр")
    print("km >= 5:", sum(map(ge5, records)), "із", len(records))
    print("km записів із from_zone == 'центр':", [r["km"] for r in records if is_center(r)])

    a, b = make_running_total(), make_running_total()
    print("a(10), a(5):", a(10), a(5), "| b(1):", b(1), "(суми незалежні)")

    kept = [r for r in records if keep(r)]
    total = make_running_total()
    last = 0
    for rec in kept:
        last = total(rec["km"])
    agg = aggregate(kept)
    print("running total:", last, "| сума aggregate:", sum(agg.values()),
          "| збігаються:", last == sum(agg.values()))
    print("classify_km:", [(km, classify_km(km)) for km in (3, 5, 19, 20, 27)])

def demo_task4(lines: list[str]) -> None:
    section("Завдання 4. Конвеєр")
    a = run_functional(lines)
    b = run_comprehension(lines)
    print("map/filter/reduce:", a)
    print("включення:        ", b)
    print("однакові:", a == b)
    print("порожній вхід:", run_functional([]), run_comprehension([]))

def demo_task5(lines: list[str]) -> None:
    section("Завдання 5. partial і каррирування")
    print("to_km(100):", to_km(100), "| to_miles(100):", to_miles(100),
          "| різні:", to_km(100) != to_miles(100))

    add3 = lambda a, b, c: a + b + c
    print("curry3(add3)(1)(2)(3) == add3(1,2,3):", curry3(add3)(1)(2)(3) == add3(1, 2, 3))
    print("curry3(add3)(1) — функція:", callable(curry3(add3)(1)))

    keep_partial = km_predicate(5)
    keep_curried = curry3(make_predicate)("km")("ge")(5)
    records = [normalize(r) for r in process(lines, now=1000.0).records]
    print("partial == keep:", [keep_partial(r) for r in records] == [keep(r) for r in records])
    print("curried == keep:", [keep_curried(r) for r in records] == [keep(r) for r in records])
    base = run_functional(lines)
    print("конвеєр з curried-предикатом такий самий:",
          run_functional(lines, keep_fn=keep_curried) == base)

def traced(lines: Iterable[str]) -> Iterator[str]:
    """Показує, скільки рядків реально прочитано."""
    for i, line in enumerate(lines, 1):
        print(f"    [прочитано рядок {i}]")
        yield line


def demo_task6_pipeline(file: Iterable[str], lines: list[str]) -> None:
    section("Завдання 6. Ліниві обчислення")
    print("-- генераторний конвеєр по відкритому файлу --")
    lazy_result = aggregate(g_keep(g_normalize(g_parse(file))))
    print("результат:", lazy_result)
    print("збігається із завданням 4:", lazy_result == run_functional(lines))

    print("-- лінивість: беремо лише перший елемент --")
    chain = g_keep(g_normalize(g_parse(traced(lines))))
    print("  перший елемент:", next(chain))

def demo_task6_generators() -> None:
    print("\n-- нескінченний потік --")
    print("islice(record_stream(), 5):")
    for rec in islice(record_stream(), 5):
        print("  ", rec)
    filtered = g_keep(g_normalize(record_stream()))
    print("islice(g_keep(g_normalize(record_stream())), 5):")
    for rec in islice(filtered, 5):
        print("  ", rec)
    # list(record_stream()) зациклився б: потік не має кінця

    print("\n-- власні генератори (без itertools) --")
    print("take(3, range(10)):", list(take(3, range(10))))
    print("drop(3, range(6)):", list(drop(3, range(6))))
    print("take_while(<4):", list(take_while(lambda x: x < 4, range(10))))
    print("chunked(2, range(5)):", list(chunked(2, range(5))))
    print("take(3) із нескінченного конвеєра:",
          [r["km"] for r in take(3, g_keep(g_normalize(record_stream())))])

    gen = take(3, range(10))
    print("перший прохід:", list(gen), "| повторний for по вичерпаному:", list(gen))

def demo_task7() -> None:
    section("Завдання 7. Калькулятор виразів (match/case)")
    cases = [
        ("Num(0)", Num(0)),
        ("Num(7)", Num(7)),
        ("Neg(Num(5))", Neg(Num(5))),
        ("(2 + 3) * 4", Mul(Add(Num(2), Num(3)), Num(4))),
        ("10 - 4", Sub(Num(10), Num(4))),
        ("9 / 3", Div(Num(9), Num(3))),
        ("2 ** 10", Pow(Num(2), 10)),
        ("sqrt(3*3 + 4*4)", Sqrt(Add(Mul(Num(3), Num(3)), Mul(Num(4), Num(4))))),
        ("Sum(1, 2, 3)", Sum((Num(1), Num(2), Num(3)))),
        ("Sum() порожня", Sum(())),
        ("2 ** -1", Pow(Num(2), -1)),
        ("sqrt(-4)", Sqrt(Num(-4))),
        ("1 / 0", Div(Num(1), Num(0))),
        ("1 / (2 - 2)", Div(Num(1), Sub(Num(2), Num(2)))),
        ("42 (не вузол)", 42),
    ]
    for label, expr in cases:
        show(label, lambda e=expr: evaluate(e))

if __name__ == "__main__":
    main()
    demo_task2(lines)
    demo_task3(lines)
    demo_task3_closures(lines)
    demo_task4(lines)
    demo_task5(lines)
    with open(DATA, encoding="utf-8") as f:
        demo_task6_pipeline(f, lines)
    demo_task6_generators()
    demo_task7()