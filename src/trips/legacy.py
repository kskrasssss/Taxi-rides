"""Вихідний код із побічними ефектами (з умови завдання 1). НЕ використовувати."""
import time

from .pipeline import parse

records = []   # глобальний стан
errors = 0     # глобальний стан


def load(path):
    global errors
    for line in open(path, encoding="utf-8"):   # ефект: відкриття файлу
        print("читаю:", line.rstrip())           # ефект: вивід
        rec = parse(line)
        if rec is None:
            errors += 1                          # ефект: зміна глобальної змінної
            continue
        rec["received_at"] = time.time()         # ефект: недетермінованість
        records.append(rec)                      # ефект: зміна глобальної змінної