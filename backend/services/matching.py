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
SUBSET_MATCH_SCORE = 0.8


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


def pick_best_match(query: str, results: list[dict], search_type: str) -> dict | None:

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

    scored = [(score(item), item) for item in results]
    best_score, best_item = max(scored, key=lambda x: x[0])
    if best_score >= SIMILARITY_THRESHOLD:
        return best_item
    return None