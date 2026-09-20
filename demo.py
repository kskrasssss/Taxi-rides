import contextlib
import io
import sys
import time
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent / "src"))

from trips import legacy
from trips.pipeline import process

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


if __name__ == "__main__":
    main()