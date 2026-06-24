# Парсер сайта → выгрузка в Google Sheets / Excel по расписанию

## Задача

Клиент хочет собирать данные с каталога (товары, цены, наличие) и видеть их
в Google Таблице без ручного копирования. Скрипт должен запускаться сам, по расписанию.

## Решение

Лёгкий Python-скрипт без фреймворков: парсит HTML через стандартный `html.parser`,
выгружает данные в CSV (offline) или в Google Sheets (production).
Никаких selenium или тяжёлых зависимостей — только то, что нужно.

## Архитектура

```
                  ┌──────────────┐
     URL / HTML ──▶  scraper/    │
                  │  parse.py    │  html.parser → список Product
                  └──────┬───────┘
                         │ list[Product]
                  ┌──────▼───────┐
                  │  scraper/    │
                  │  exporter.py │  Exporter (ABC)
                  └──────┬───────┘
              ┌──────────┴──────────┐
              ▼                     ▼
        CsvExporter          GoogleSheetsExporter
        (stdlib, offline)    (gspread, production)
              │                     │
      output_demo.csv       Google Таблица (Sheets API)
```

**Модули:**

| Файл | Роль |
|---|---|
| `scraper/models.py` | Датакласс `Product` (сериализация строк) |
| `scraper/parse.py` | `parse_products(html)` — чистая функция, без сети |
| `scraper/exporter.py` | `Exporter` ABC + `CsvExporter` + `GoogleSheetsExporter` |
| `fetch.py` | Production-фетчер на `httpx` (сеть + парсинг) |
| `demo.py` | Offline-демо без зависимостей |

## Демо без настройки

Работает из коробки — никаких ключей и интернета:

```bash
python3 demo.py
```

Парсит `sample_products.html` (5 товаров), печатает таблицу и сохраняет `output_demo.csv`.

## Запуск реального парсера

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Создайте `.env` из `.env.example` и укажите путь к ключу service account и ID таблицы.

3. Запустите:

```python
from dotenv import load_dotenv
load_dotenv()

from fetch import fetch_and_parse
from scraper.exporter import GoogleSheetsExporter

products = fetch_and_parse("https://example.com/catalog")
exporter = GoogleSheetsExporter()
url = exporter.export(products)
print(f"Таблица обновлена: {url}")
```

## Планировщик (cron)

Добавьте в `crontab -e` для запуска каждую ночь в 03:00:

```cron
0 3 * * * /usr/bin/python3 /path/to/web-scraper-to-sheets/run_production.py >> /var/log/scraper.log 2>&1
```

Или используйте systemd timer / GitHub Actions для облачного варианта.

## Стек

- **Python 3.10+** — `html.parser`, `csv`, `dataclasses` (stdlib, демо)
- **httpx** — HTTP-клиент (синхронный API) для production-скачивания
- **gspread + google-auth** — запись в Google Sheets через service account
- **cron / systemd** — планировщик
