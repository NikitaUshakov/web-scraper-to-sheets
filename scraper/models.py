"""
Модели данных: датаклассы для записей, извлечённых парсером.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    """Одна товарная позиция со страницы каталога."""
    name: str
    price: float          # цена в рублях
    currency: str         # символ валюты, по умолчанию ₽
    availability: str     # «В наличии» / «Нет в наличии» / «Под заказ»
    category: str = ""
    url: str = ""

    def to_row(self) -> list:
        """Сериализация в список для CSV / Google Sheets."""
        return [
            self.name,
            f"{self.price:.2f}",
            self.currency,
            self.availability,
            self.category,
            self.url,
        ]

    @staticmethod
    def csv_headers() -> list[str]:
        return ["Название", "Цена", "Валюта", "Наличие", "Категория", "URL"]
