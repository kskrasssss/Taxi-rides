from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import reduce
from typing import Any, Callable, Iterable

from .hof import make_predicate, normalize   # normalize/make_predicate уже готові в hof.py (завд. 3) — не дублюємо їх тут

Rec = dict[str, Any]                # "псевдонім типу": запис — це звичайний словник
Predicate = Callable[[Rec], bool]   # тип "функція від запису до True/False"

FIELDS = ("from_zone", "to_zone", "km", "minutes")   # порядок полів у рядку файлу — саме такий


def _is_int(text: str) -> bool:
    # допоміжна перевірка: чи можна рядок перетворити на int, без побічних ефектів (без print/файлів)
    try:
        int(text)
    except ValueError:
        return False
    return True


def parse(line: str) -> Rec | None:
    # ЧИСТА функція: тільки рядок -> словник або None, нічого зовнішнього не чіпає
    parts = line.rstrip("\n").split(";")
    if len(parts) != len(FIELDS):          # не 4 поля -> некоректний рядок
        return None
    from_zone, to_zone, km, minutes = parts
    if not from_zone.strip() or not to_zone.strip():   # порожня зона (навіть із пробілів) -> некоректно
        return None
    if not (_is_int(km) and _is_int(minutes)):         # km/minutes не число -> некоректно
        return None
    return dict(zip(FIELDS, parts))   # значення тут ще "сирі" (з пробілами, рядками) — нормалізація окремим кроком


@dataclass(frozen=True)
class Result:
    # незмінний контейнер результату: замість того, щоб process() змінював щось ззовні, вона повертає такий об'єкт
    records: tuple[Rec, ...]   # кортеж, а не список — теж натяк на незмінність
    errors: int


def process(lines: Iterable[str], now: float) -> Result:
    # ЧИСТА функція: приймає вже готові рядки й ЧАС ЗОВНІ (now), сама не читає час і нічого не друкує
    parsed = [parse(line) for line in lines]
    # кожному вдалому запису додаємо received_at=now; {**rec, ...} створює НОВИЙ словник, rec не мутується
    good = tuple({**rec, "received_at": now} for rec in parsed if rec is not None)
    errors = sum(rec is None for rec in parsed)   # True/False рахуються як 1/0, тому sum() рахує кількість None
    return Result(records=good, errors=errors)


def normalize_plain(rec: Rec) -> Rec:
    # "звичайна" (не через compose/pipe) версія нормалізації — для порівняння в завданні 3
    return {
        **rec,
        "from_zone": rec["from_zone"].strip().lower(),   # категорійне поле: прибрати пробіли + нижній регістр
        "to_zone": rec["to_zone"].strip(),
        "km": int(rec["km"]),       # числові поля -> int
        "minutes": int(rec["minutes"]),
    }


THRESHOLD = 5   # поріг відбору за умовою лаби (можна узгодити з викладачем)

# готовий предикат keep = "km >= 5", зібраний через фабрику з hof.py (замикання, завдання 3.3)
keep: Predicate = make_predicate("km", "ge", THRESHOLD)


def add_to_groups(acc: dict[str, int], rec: Rec) -> dict[str, int]:
    # функція-акумулятор для reduce: додає km поїздки до групи from_zone
    # повертає НОВИЙ словник (immutable-стиль), а не мутує acc на місці
    key = rec["from_zone"]
    return {**acc, key: acc.get(key, 0) + rec["km"]}


def aggregate(records: Iterable[Rec]) -> dict[str, int]:
    # reduce "згортає" послідовність записів в один словник {зона: сума km}, починаючи з порожнього {}
    return reduce(add_to_groups, records, {})


def run_functional(lines: Iterable[str], keep_fn: Predicate = keep) -> dict[str, int]:
    # СПОСІБ A (завд. 4.1): map/filter/reduce. map і filter у Python 3 ЛІНИВІ — повертають ітератори,
    # тому до виклику reduce нічого насправді ще не обчислено
    parsed = filter(lambda rec: rec is not None, map(parse, lines))
    normalized = map(normalize, parsed)
    kept = filter(keep_fn, normalized)   # keep_fn параметром — щоб завд. 5.3 могло підставити каррирований предикат
    return reduce(add_to_groups, kept, {})


def run_comprehension(lines: Iterable[str], keep_fn: Predicate = keep) -> dict[str, int]:
    # СПОСІБ B (завд. 4.2): спискові включення. На відміну від способу A, ЖАДІБНИЙ —
    # кожен [... for ...] одразу будує повний список у пам'яті
    parsed = [rec for line in lines if (rec := parse(line)) is not None]   # := "морж" — присвоює й перевіряє за раз
    normalized = [normalize(rec) for rec in parsed]
    kept = [rec for rec in normalized if keep_fn(rec)]
    totals: Counter[str] = Counter()   # Counter — словник із дефолтним значенням 0, зручний для підсумовування
    for rec in kept:
        totals[rec["from_zone"]] += rec["km"]
    return dict(totals)