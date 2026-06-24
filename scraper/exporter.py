"""
Экспортеры результатов парсинга.

Архитектура:
  Exporter (ABC)
    ├── CsvExporter      — только stdlib, работает offline
    └── GoogleSheetsExporter — требует gspread + google-auth (lazy import)
"""
import csv
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from scraper.models import Product

if TYPE_CHECKING:
    import gspread  # только для аннотаций, не импортируется в рантайме


class Exporter(ABC):
    """Базовый интерфейс: принимает список продуктов, куда-то выгружает."""

    @abstractmethod
    def export(self, products: list[Product]) -> str:
        """
        Выгружает данные.
        Возвращает строку-дескриптор результата (путь к файлу, URL таблицы…).
        """


# ------------------------------------------------------------------ #
#  CSV-экспортёр (stdlib, zero dependencies)
# ------------------------------------------------------------------ #

class CsvExporter(Exporter):
    """Сохраняет данные в CSV-файл через стандартный модуль csv."""

    def __init__(self, output_path: str | Path = "output.csv") -> None:
        self.output_path = Path(output_path)

    def export(self, products: list[Product]) -> str:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(Product.csv_headers())
            for p in products:
                writer.writerow(p.to_row())
        return str(self.output_path.resolve())


# ------------------------------------------------------------------ #
#  Google Sheets-экспортёр (gspread, lazy import)
# ------------------------------------------------------------------ #

class GoogleSheetsExporter(Exporter):
    """
    Записывает данные в Google Таблицу.

    Параметры берутся из переменных окружения:
      GOOGLE_CREDS_FILE   — путь к service-account JSON
      SPREADSHEET_ID      — ID таблицы из URL
      WORKSHEET_NAME      — имя листа (по умолчанию «Sheet1»)

    Требует: pip install gspread google-auth
    """

    def __init__(
        self,
        creds_file: str | None = None,
        spreadsheet_id: str | None = None,
        worksheet_name: str = "Sheet1",
    ) -> None:
        self.creds_file = creds_file or os.environ["GOOGLE_CREDS_FILE"]
        self.spreadsheet_id = spreadsheet_id or os.environ["SPREADSHEET_ID"]
        self.worksheet_name = worksheet_name

    def _get_client(self):
        """Lazy-импорт gspread: библиотека нужна только при реальной выгрузке."""
        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except ImportError as e:
            raise ImportError(
                "Установите зависимости: pip install gspread google-auth"
            ) from e

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(self.creds_file, scopes=scopes)
        return gspread.authorize(creds)

    def export(self, products: list[Product]) -> str:
        client = self._get_client()
        sheet = client.open_by_key(self.spreadsheet_id)
        worksheet = sheet.worksheet(self.worksheet_name)

        # Очищаем лист и пишем заново (idempotent)
        rows = [Product.csv_headers()] + [p.to_row() for p in products]
        worksheet.clear()
        worksheet.update(rows)

        url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
        return url
