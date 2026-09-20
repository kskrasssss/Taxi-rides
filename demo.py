import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

DATA = Path(__file__).parent / "data" / "trips.txt"


def section(title: str) -> None:
    print(f"\n{'=' * 8} {title} {'=' * 8}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # щоб кирилиця не ламалась у консолі Windows


if __name__ == "__main__":
    main()