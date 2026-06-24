"""
Production-запуск по расписанию (cron): скачать страницу → распарсить → выгрузить в Google Sheets.
Настройки берутся из .env: GOOGLE_CREDS_FILE, SPREADSHEET_ID, WORKSHEET_NAME, TARGET_URL.

Пример cron (каждую ночь в 03:00):
  0 3 * * * /usr/bin/python3 /path/to/web-scraper-to-sheets/run_production.py >> scraper.log 2>&1
"""
import os

from dotenv import load_dotenv

from fetch import fetch_and_parse
from scraper.exporter import GoogleSheetsExporter


def main() -> None:
    load_dotenv()
    url = os.environ["TARGET_URL"]
    products = fetch_and_parse(url)
    sheet_url = GoogleSheetsExporter().export(products)
    print(f"Готово: {len(products)} товаров → {sheet_url}")


if __name__ == "__main__":
    main()
