import json
import os

import requests
COLES_SEARCH_URL = (
    "https://coles-product-price-api.p.rapidapi.com/coles/product-search/"
)
RAPIDAPI_HOST = "coles-product-price-api.p.rapidapi.com"


def _on_special(item: dict, current_price: float) -> bool:
    was_price = item.get("was_price")
    if was_price is None:
        was_price = item.get("original_price")
    if was_price is None:
        return False
    try:
        return current_price < float(was_price)
    except (TypeError, ValueError):
        return False


def search_item(query: str) -> list[dict]:
    """Search Coles catalog; return up to 3 normalized product dicts."""
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return []

    try:
        response = requests.get(
            COLES_SEARCH_URL,
            params={"query": query, "page_size": 3},
            headers={
                "x-rapidapi-host": RAPIDAPI_HOST,
                "x-rapidapi-key": api_key,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        print(f"[Coles API] query={query!r}")
        print(json.dumps(data, indent=2))
    except (requests.RequestException, ValueError):
        return []

    results = []
    for item in data.get("results", [])[:3]:
        current_price = float(item.get("current_price", 0))
        results.append(
            {
                "name": item.get("product_name", ""),
                "brand": item.get("product_brand", ""),
                "price": current_price,
                "size": item.get("product_size", ""),
                "on_special": _on_special(item, current_price),
            }
        )
    return results
