import contextlib
import io
import sys
import time
from pathlib import Path
from typing import Callable

from dataclasses import dataclass

from trips import legacy
from trips.model import Record, add_km, to_record, with_to_zone
from trips.pipeline import normalize, process

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


if __name__ == "__main__":
    main()