from django.conf import settings
from django.core.cache import cache

import httpx

__all__ = (
    "fetch_news",
    "fetch_news_detail",
)


def _news_url(lang: str) -> str:
    return f"{settings.NEWS_API_URL}/{lang}/api/v1/blogdetail/news/"


def fetch_news(page: int = 1, lang: str = "ru", category: int | None = None):
    cache_key = f"news:{lang}:{page}:{category}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {"page": page}
    if category:
        params["category"] = category

    with httpx.Client(timeout=10) as client:
        resp = client.get(_news_url(lang), params=params)
        resp.raise_for_status()

    data = resp.json()
    cache.set(cache_key, data, timeout=300)
    return data


def fetch_news_detail(news_id: int, lang: str = "ru"):
    cache_key = f"news_detail:{lang}:{news_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    with httpx.Client(timeout=10) as client:
        resp = client.get(f"{_news_url(lang)}{news_id}/detail/")
        resp.raise_for_status()

    data = resp.json()
    cache.set(cache_key, data, timeout=600)
    return data
