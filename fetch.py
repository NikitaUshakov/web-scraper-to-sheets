"""
Реальный HTTP-фетчер на базе httpx.
Используется в production-запуске (не в offline-демо).

Зависимости: pip install httpx
"""
import httpx
from scraper.parse import parse_products
from scraper.models import Product


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ProductScraper/1.0; "
        "+https://github.com/your-handle/web-scraper-to-sheets)"
    )
}


def fetch_and_parse(url: str, timeout: float = 15.0) -> list[Product]:
    """
    Скачивает страницу по URL и возвращает список товаров.
    Вся логика парсинга — в scraper/parse.py (чистая функция).
    """
    with httpx.Client(headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
    return parse_products(response.text)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python3 fetch.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    products = fetch_and_parse(url)
    for p in products:
        print(p)
