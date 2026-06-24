"""
Парсинг HTML-разметки страницы каталога товаров.
Зависимости только стандартная библиотека — модуль можно использовать
и в offline-демо, и в production (где HTML получают через httpx).
"""
from html.parser import HTMLParser
from typing import Optional
from scraper.models import Product


class _ProductParser(HTMLParser):
    """
    Конечный автомат, разбирающий шаблонный HTML каталога.
    Структура разметки:
      <div class="product-card">
        <h2 class="product-name">...</h2>
        <span class="product-price">1 299.00</span>
        <span class="product-currency">₽</span>
        <span class="product-avail">В наличии</span>
        <span class="product-category">Электроника</span>
        <a class="product-link" href="/item/123">подробнее</a>
      </div>
    """

    def __init__(self) -> None:
        super().__init__()
        self.products: list[Product] = []

        # текущая карточка (None = вне карточки)
        self._current: Optional[dict] = None
        # какое поле сейчас собираем
        self._capture: Optional[str] = None

    # ------------------------------------------------------------------ #
    #  Вспомогательные методы
    # ------------------------------------------------------------------ #

    def _class_of(self, attrs: list) -> str:
        """Возвращает значение атрибута class или пустую строку."""
        for name, val in attrs:
            if name == "class":
                return val or ""
        return ""

    def _href_of(self, attrs: list) -> str:
        for name, val in attrs:
            if name == "href":
                return val or ""
        return ""

    # ------------------------------------------------------------------ #
    #  Обработчики HTMLParser
    # ------------------------------------------------------------------ #

    def handle_starttag(self, tag: str, attrs: list) -> None:
        cls = self._class_of(attrs)

        if tag == "div" and cls == "product-card":
            # начинаем новую карточку
            self._current = {
                "name": "",
                "price": 0.0,
                "currency": "₽",
                "availability": "",
                "category": "",
                "url": "",
            }
            return

        if self._current is None:
            return  # вне карточки — пропускаем

        # открывающие теги внутри карточки
        if tag == "h2" and cls == "product-name":
            self._capture = "name"
        elif tag == "span" and cls == "product-price":
            self._capture = "price"
        elif tag == "span" and cls == "product-currency":
            self._capture = "currency"
        elif tag == "span" and cls == "product-avail":
            self._capture = "availability"
        elif tag == "span" and cls == "product-category":
            self._capture = "category"
        elif tag == "a" and cls == "product-link":
            self._current["url"] = self._href_of(attrs)
            self._capture = None

    def handle_endtag(self, tag: str) -> None:
        # закрываем карточку
        if tag == "div" and self._current is not None:
            d = self._current
            # защита от пустых/неполных карточек
            if d["name"]:
                self.products.append(
                    Product(
                        name=d["name"].strip(),
                        price=d["price"],
                        currency=d["currency"].strip(),
                        availability=d["availability"].strip(),
                        category=d["category"].strip(),
                        url=d["url"].strip(),
                    )
                )
            self._current = None
        self._capture = None

    def handle_data(self, data: str) -> None:
        if self._current is None or self._capture is None:
            return
        text = data.strip()
        if not text:
            return
        field = self._capture
        if field == "price":
            # убираем пробелы-разделители тысяч, заменяем запятую на точку
            cleaned = text.replace(" ", "").replace(" ", "").replace(",", ".")
            try:
                self._current["price"] = float(cleaned)
            except ValueError:
                self._current["price"] = 0.0
        else:
            self._current[field] = text


# ------------------------------------------------------------------ #
#  Публичная функция
# ------------------------------------------------------------------ #

def parse_products(html: str) -> list[Product]:
    """
    Принимает HTML-строку, возвращает список Product.
    Без сетевых вызовов — чистая функция, удобна для тестов.
    """
    parser = _ProductParser()
    parser.feed(html)
    return parser.products
