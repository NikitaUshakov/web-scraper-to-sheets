"""
Offline-демо: парсим локальный HTML-файл и экспортируем в CSV.
Зависимости: ТОЛЬКО стандартная библиотека Python 3.10+.
Сеть не нужна.

Запуск:
    python3 demo.py
"""
import sys
import os
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы пакет scraper нашёлся
# независимо от рабочей директории запуска
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from scraper.parse import parse_products
from scraper.exporter import CsvExporter

# ------------------------------------------------------------------ #
#  Пути
# ------------------------------------------------------------------ #
FIXTURE = PROJECT_ROOT / "sample_products.html"
OUTPUT_CSV = PROJECT_ROOT / "output_demo.csv"


def main() -> None:
    # 1. Читаем HTML-фикстуру
    html = FIXTURE.read_text(encoding="utf-8")

    # 2. Парсим товары (чистая функция, без сети)
    products = parse_products(html)

    # 3. Выводим результат в терминал
    print(f"{'='*60}")
    print(f"  Найдено товаров: {len(products)}")
    print(f"{'='*60}")
    header = f"{'Название':<40} {'Цена':>10}  {'Валюта':<6}  Наличие"
    print(header)
    print("-" * len(header))
    for p in products:
        print(f"{p.name:<40} {p.price:>10,.2f}  {p.currency:<6}  {p.availability}")

    # 4. Экспортируем в CSV (stdlib — никаких внешних библиотек)
    exporter = CsvExporter(output_path=OUTPUT_CSV)
    csv_path = exporter.export(products)

    print(f"\nCSV сохранён → {csv_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
