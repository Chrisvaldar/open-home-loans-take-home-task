import re
from difflib import SequenceMatcher

BRAND_LIST = [
    "a2",
    "devondale",
    "bega",
    "sanitarium",
    "vegemite",
    "weet-bix",
    "uncle tobys",
    "maggi",
    "heinz",
    "campbell",
    "pampas",
    "tip top",
    "wonder white",
    "helgas",
    "nescafe",
    "milo",
    "up&go",
]

SIMILARITY_THRESHOLD = 0.15
GENERIC_SIMILARITY_THRESHOLD = 0.25
SUBSET_MATCH_SCORE = 0.8

STAPLE_INTENT_MAP = {
    "milk": "full cream milk 2L",
    "bread": "white sandwich bread loaf",
    "eggs": "free range eggs 700g",
    "butter": "butter 500g",
    "chicken": "chicken breast",
    "mince": "beef mince 500g",
    "rice": "white rice 1kg",
    "pasta": "pasta 500g",
    "cheese": "tasty cheese 500g",
    "yoghurt": "greek yoghurt",
}

HOMEBRAND_KEYWORDS = (
    "woolworths",
    "coles",
    "homebrand",
    "select",
    "essentials",
    "smart buy",
    "macro",
    "simply",
)

RECEIPT_STORE_PREFIX = re.compile(r"^(?:coles|woolworths|ww)\s+", re.IGNORECASE)
RECEIPT_SIZE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:kg|g|gram|grams|ml|l|litre|litres|pack|pk|each|perkg)\b",
    re.IGNORECASE,
)
RECEIPT_PACK_COUNT = re.compile(r"\b\d+\s*pack\b", re.IGNORECASE)

EXCLUDED_BAG_PHRASES = (
    "reusable bag",
    "shopping bag",
    "carry bag",
    "plastic bag",
)


def is_excluded_compare_item(item: str) -> bool:
    """True for store bag levy lines that should not be price-compared."""
    text = item.strip().lower()
    if not text:
        return True
    return any(phrase in text for phrase in EXCLUDED_BAG_PHRASES)


def filter_comparable_items(items: list[str]) -> list[str]:
    return [item for item in items if not is_excluded_compare_item(item)]


def normalize_receipt_search_query(item: str) -> str:
    """Turn a raw receipt line into a cleaner store search query."""
    text = item.strip()
    text = RECEIPT_STORE_PREFIX.sub("", text)
    text = re.sub(r"[:/]", " ", text)
    text = RECEIPT_SIZE.sub("", text)
    text = RECEIPT_PACK_COUNT.sub("", text)
    text = re.sub(r"\bperkg\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\ble\b", "lean", text, flags=re.IGNORECASE)
    text = re.sub(r"\bcap\b", "tablets", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text or item.strip().lower()


def expand_staple_query(query: str) -> str:
    """Expand common single-word staples to a more specific search term."""
    key = query.strip().lower()
    return STAPLE_INTENT_MAP.get(key, query)


def is_staple_query(query: str) -> bool:
    return query.strip().lower() in STAPLE_INTENT_MAP


def store_staple_search_term(base_term: str, store: str) -> str:
    """Prefix staple searches with the store name to surface homebrand products."""
    if store == "woolworths":
        return f"woolworths {base_term}"
    if store == "coles":
        return f"coles {base_term}"
    return base_term


def detect_search_type(query: str) -> str:
    """Return 'branded' if query contains a known brand word as a separate word, else 'generic'."""
    query_lower = query.lower()
    for brand in sorted(BRAND_LIST, key=len, reverse=True):
        pattern = r"\b" + re.escape(brand) + r"\b"
        if re.search(pattern, query_lower):
            return "branded"
    return "generic"


def _brand_in_query(query: str) -> str | None:
    query_lower = query.lower()
    for brand in sorted(BRAND_LIST, key=len, reverse=True):
        pattern = r"\b" + re.escape(brand) + r"\b"
        if re.search(pattern, query_lower):
            return brand
    return None


def normalise_unit_price(price: float, size: str) -> tuple[float, str] | None:
    """Parse size string and return (unit_price, unit_label) or None."""
    if not size or not size.strip():
        return None

    size_clean = size.strip().lower()

    # Multipack format: e.g., "6x200ml" or "4 x 125 g"
    multipack_match = re.match(r"^(\d+)\s*[x×*]\s*([\d.]+)\s*(l|ml|kg|g)$", size_clean)
    if multipack_match:
        count = int(multipack_match.group(1))
        amount_per = float(multipack_match.group(2))
        unit = multipack_match.group(3)
        if unit in ("l", "ml"):
            total_ml = amount_per * count * (1000 if unit == "l" else 1) #CHECK: price from API for whole pack or singular?
            if total_ml <= 0:
                return None
            return (price / total_ml * 100, "per 100ml")
        elif unit in ("kg", "g"):
            total_g = amount_per * count * (1000 if unit == "kg" else 1)
            if total_g <= 0:
                return None
            return (price / total_g * 100, "per 100g")
        else:
            return None

    # Try to extract just the numeric size & unit, allowing for optional prefixes/suffixes, e.g. "approx 500g", "500g (approx)"
    simple_match = re.search(r"([\d.]+)\s*(l|ml|kg|g)", size_clean)
    if simple_match:
        amount = float(simple_match.group(1))
        unit = simple_match.group(2)
        if unit in ("l", "ml"):
            ml = amount * (1000 if unit == "l" else 1)
            if ml <= 0:
                return None
            return (price / ml * 100, "per 100ml")
        elif unit in ("kg", "g"):
            grams = amount * (1000 if unit == "kg" else 1)
            if grams <= 0:
                return None
            return (price / grams * 100, "per 100g")
        else:
            return None

    return None
    
def _query_words(query: str) -> set[str]:
    return set(re.findall(r"\b\w+\b", query.lower()))


def _similarity_score(query: str, target: str) -> float:
    """Score query against a single text field (name or brand)."""
    if not target:
        return 0.0

    query_lower = query.lower()
    target_lower = target.lower()
    query_word_set = _query_words(query_lower)
    target_word_set = _query_words(target_lower)

    if query_word_set and query_word_set <= target_word_set:
        coverage = len(query_word_set) / len(target_word_set)
        if coverage >= 0.5:
            return SUBSET_MATCH_SCORE
        # coverage too low -> fall through to SequenceMatcher

    return SequenceMatcher(None, query_lower, target_lower).ratio()


def _query_word_in_name(query: str, name: str) -> bool:
    """Return True if at least one query word appears in the product name."""
    return bool(_query_words(query) & _query_words(name))


def _is_single_word_query(query: str) -> bool:
    return len(_query_words(query)) == 1


def _is_homebrand(item: dict) -> bool:
    text = f"{item.get('name', '')} {item.get('brand', '')}".lower()
    return any(keyword in text for keyword in HOMEBRAND_KEYWORDS)


def pick_best_match(
    query: str,
    results: list[dict],
    search_type: str,
    search_term: str | None = None,
) -> dict | None:

    def score(item):
        """Score name first, then brand; take the better of the two."""
        name_score = _similarity_score(query, item.get("name", ""))
        brand_score = _similarity_score(query, item.get("brand", ""))
        return max(name_score, brand_score)

    if search_type == "branded":
        brand = _brand_in_query(query)
        if not brand:
            return None
        # Filter results where brand is in product name or brand field
        filtered = []
        for item in results:
            name = item.get("name", "").lower()
            prod_brand = item.get("brand", "").lower()
            pattern = r"\b" + re.escape(brand) + r"\b"
            if re.search(pattern, name) or re.search(pattern, prod_brand):
                filtered.append(item)
        if not filtered:
            return None
        best_item = max(filtered, key=score)
        return best_item

    if not results:
        return None

    match_query = (search_term or query).strip()
    candidates = results
    if _is_single_word_query(match_query):
        candidates = [
            item
            for item in results
            if _query_word_in_name(match_query, item.get("name", ""))
        ]
        if not candidates:
            return None

    def generic_score(item):
        return _similarity_score(match_query, item.get("name", ""))

    passing = [
        item
        for item in candidates
        if generic_score(item) >= GENERIC_SIMILARITY_THRESHOLD
    ]
    if not passing:
        return None

    homebrand_matches = [item for item in passing if _is_homebrand(item)]
    pool = homebrand_matches if homebrand_matches else passing
    return min(pool, key=lambda item: item.get("price", float("inf")))