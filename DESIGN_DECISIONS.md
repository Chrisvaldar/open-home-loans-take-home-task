# Design Decisions

A running log of product and engineering choices for **Frugl**. Add new entries here whenever a meaningful decision is made or revisited.

---

## Product identity

### App renamed to Frugl

**Decision:** Product name is **Frugl** (was "Smart Shopping Destination" in scaffold).

**Why:** Shorter consumer-facing brand for the price-comparison app. Updated in `frontend/index.html` title, `App.jsx` header and shield icon alt text, and `backend/main.py` FastAPI title.

---

## Architecture and stack

### Vite + React instead of Next.js

**Decision:** Keep the existing Vite + React SPA rather than migrating to Next.js.

**Why:** The app is a single-user comparison flow (list, loading, results) with no SEO requirement. Vite was already scaffolded with Tailwind, a dev proxy, and `api.js`. Next.js would add routing and deployment complexity without clear benefit for this assessment scope.

**Reference:** [PROJECT_STATE.md](PROJECT_STATE.md) section 2.

---

### FastAPI backend with a REST boundary

**Decision:** All Woolworths, Coles, and Gemini calls run server-side. The frontend only talks to `/api/compare` and `/api/receipt`.

**Why:** Protects API keys (`RAPIDAPI_KEY`, `GEMINI_API_KEY`), keeps matching and comparison logic testable in Python, and separates UI from data orchestration.

---

### View state in `App.jsx` (no React Router)

**Decision:** Use `useState` for `view` (`list` | `loading` | `results` | `error`) rather than URL-based routing.

**Why:** Four screens with linear flow. Router adds boilerplate without user benefit for a demo SPA.

---

## Data and external APIs

### Live RapidAPI pricing for both stores

**Decision:** Woolworths and Coles product search both go through RapidAPI (data-holdings-group), one `RAPIDAPI_KEY`, `page_size=3` per search.

**Why:** Same interface for both chains; free tier sufficient for demo. Take top 3 results and pick the best match rather than blindly using rank 1.

---

### Google Gemini for receipt OCR

**Decision:** Receipt images are sent to `gemini-2.5-flash` via `google-genai`; returns a JSON array of item strings.

**Why:** Receipt scanning was added after the initial brief. Gemini handles varied receipt layouts better than hand-rolled OCR. Failures return `[]` rather than crashing the endpoint.

---

### No caching, auth, or rate limiting (assessment scope)

**Decision:** Each compare hits live APIs synchronously per item per store. No user accounts.

**Why:** Acceptable for a take-home demo. Documented as a known limitation in [PROJECT_STATE.md](PROJECT_STATE.md).

---

### Special badge: API detection plus cross-store inference

**Decision:** Surface a yellow **Special** badge in results when `on_special` is true. Detection uses two layers:

1. **Primary (store search):** In `woolworths.py` and `coles.py`, set `on_special` when the API item includes `was_price` or `original_price` and `current_price` is lower than that value. If neither field exists, leave `on_special` false at this stage.
2. **Fallback (compare):** In `compare.py`, `_infer_cross_store_special()` marks the cheaper store as on special when both stores matched the same brand and pack size and one price is at least 15% lower than the other.

**Why:** Live RapidAPI search responses for Woolworths and Coles typically only return `current_price`, name, brand, size, and URL. They do not include `was_price`, `original_price`, or `on_special`, so the primary check alone never fires. Without the fallback, the badge would never appear despite obvious gaps like Kirk's lemonade at $1.80 vs $3.00.

**Caveat:** The fallback is an inference, not a fact. A large cross-store price gap might mean a weekly special, but it could also be a permanent shelf-price difference, a data lag, or mismatched promo timing. We label the badge **Special** (not "On special") to keep the wording neutral. If the APIs later expose reliable was/original pricing, prefer that and treat inference as a last resort only.

**Reference:** [`backend/services/woolworths.py`](backend/services/woolworths.py), [`backend/services/coles.py`](backend/services/coles.py), [`backend/services/compare.py`](backend/services/compare.py), [`frontend/src/components/Results.jsx`](frontend/src/components/Results.jsx).

---

### Groq reranker for receipt items

**Decision:** When `compare_basket(..., source="receipt")`, pick store matches via `rerank_with_groq()` (`llama-3.1-8b-instant`, `GROQ_API_KEY`) instead of string matching. Receipt lines are normalized with `normalize_receipt_search_query()` before API search; up to 10 candidates per store.

**Why:** Receipt OCR lines are noisy; string matcher picked cheapest partial overlap (gravy for Somat, beer for beef). Groq reads receipt line plus numbered candidates and returns an index or `-1`.

**Strict matching (2026-05-27):** Default to `-1` unless product type, brand, size, and name all align. Rejects pet food, wrong variants, denture tablets, etc.

**Produce exception (2026-05-27):** Fresh produce (fruit, vegetable, meat) may match when core ingredient aligns even if word order differs or sold by each/kg (e.g. `brown onions` → `Onion Brown each $0.63`). Prevents Woolworths loose produce being rejected while gravy/wine candidates are in the pool.

**Produce-specific rules (2026-05-27):** `is_produce_query()` detects produce keywords (onion, cabbage, beef, etc.). When true, the Groq prompt adds stricter rules: reject processed/packaged candidates (gravy, mix, tin, sauce, wine, soup, pet, dog); require same variety (green cabbage not wombok/savoy/red; brown onion not spring onion/shallot); return `-1` if no clear fresh match.

**Reference:** [`backend/services/groq_reranker.py`](backend/services/groq_reranker.py), [`backend/tests/test_groq_reranker.py`](backend/tests/test_groq_reranker.py), [`backend/services/receipt.py`](backend/services/receipt.py) (Gemini search-friendly extraction).

---

### Receipt JSON parsing (markdown fences)

**Decision:** Parse Gemini output with `_parse_items_json()`, which strips optional markdown code fences before `json.loads`. Log raw response and parsed item count to stdout.

**Why:** Gemini often wraps the array in ` ```json ` despite the prompt. Bare `json.loads()` failed silently and returned `[]`, showing "No items found on receipt" even when extraction worked.

**Reference:** [`backend/services/receipt.py`](backend/services/receipt.py), [`backend/tests/test_receipt_parse.py`](backend/tests/test_receipt_parse.py).

---

### Per-row winner savings in Results

**Decision:** In the breakdown table (and mobile cards), show `Saves $X.XX` at the start of the NOTE column (via `MatchNote`), before the match note and confidence. Hidden when `saving` is 0. Winner column shows store logo only (no duplicate store name text).

**Why:** Makes per-item value visible without cluttering the winner cell. Logo alone is enough to identify the store.

**Reference:** [`frontend/src/components/Results.jsx`](frontend/src/components/Results.jsx) `WinnerCell`, [`frontend/src/components/MatchNote.jsx`](frontend/src/components/MatchNote.jsx).

---

## Product matching

### Two paths: branded vs generic

**Decision:** `detect_search_type()` checks a hardcoded brand list (17 brands). Branded queries filter results to products whose name or brand contains that brand word. Generic queries (e.g. `"milk"`, `"bread"`) compare across whatever brand the matcher selects at each store.

**Why:** Branded items (e.g. `"a2 milk 2L"`) must not silently substitute a different brand. Generic items intentionally allow different homebrand products per store, with a note in the response.

---

### String matching for product selection (and its failure mode)

**Decision:** Use word-subset boosting plus `difflib.SequenceMatcher` to score API candidates, not embeddings or an LLM reranker (for now).

**Why:** Zero extra latency or cost; good enough for branded queries and multi-word generic queries. Implemented entirely in stdlib.

**Problem observed:** Generic query `"bread"` matched Coles product **"Inspired Mud Cake"** because the brand field was **"Fairy Bread"**. Scoring took `max(name_score, brand_score)`, so the brand hit scored 0.8 via word-subset match even though the product name had nothing to do with bread.

**Fix (2026-05-27):** Three targeted changes to generic matching only:

1. Score against **product name only**, never brand.
2. For **single-word** generic queries, require at least one query word in the product **name**. If no candidate passes, return `None` (no_match) instead of a bad pick.
3. Generic similarity threshold via `GENERIC_SIMILARITY_THRESHOLD` (see history below).

Branded query logic was not changed.

**Update (2026-05-27):** Threshold 0.4 caused asymmetric results: Coles short names (e.g. `"Light Milk"`) passed while longer Woolworths names scored below threshold and returned no_match. Lowered generic threshold to **0.25**.

---

### Staple intent map for vague single-word queries

**Decision:** Before calling the store search APIs, expand exact single-word staples via `STAPLE_INTENT_MAP` in `matching.py` (e.g. `"milk"` to `"full cream milk 2L"`, `"bread"` to `"white sandwich bread loaf"`). Original list item text is kept for display and for `pick_best_match`; only the API search term changes.

**Why:** Shoppers typing `"bread"` or `"milk"` usually mean a standard loaf or homebrand milk, not Turkish bread or premium a2. String matching alone cannot infer that. A small curated map (~10 staples) is explicit, testable, and aligned with finding cheaper comparable products.

**Implementation:** `expand_staple_query()` in `matching.py`; called from `compare_basket()` before `search_woolworths` / `search_coles`.

**Update (2026-05-27):** Generic matching now uses the expanded `search_term` (not the original single word) when scoring and filtering API results. That fixes Woolworths `"Not found"` when the expanded search returns products whose names match `"white sandwich bread loaf"` but not the lone word `"bread"`.

---

### Cheapest homebrand preference for generic matches

**Decision:** Among generic candidates that pass the similarity threshold, prefer products whose name or brand contains a homebrand keyword (`woolworths`, `coles`, `homebrand`, `select`, etc.). From that pool, pick the **lowest pack price**. If no homebrand candidate qualifies, pick the cheapest overall.

**Why:** The app compares weekly shop cost. Premium matches (e.g. a2 milk at $6.90) are valid string matches but wrong for a vague `"milk"` list item. Shoppers without context usually mean the cheapest comparable staple.

**Scope:** Generic path only; branded queries unchanged.

**Update (2026-05-27):** Generic staple queries (e.g. `"milk"`) now search each store with a store-prefixed term (`"woolworths full cream milk 2L"`, `"coles full cream milk 2L"`) so homebrand products appear in API results. Without this, a generic search returned national brands (Dairy Farmers, Devondale) that pass matching but are not the cheapest own-brand lines.

---

### Word-subset boost for short generic queries

**Decision:** If all query words appear in the target string and word coverage is at least 50%, score 0.8 instead of relying on SequenceMatcher alone.

**Why:** SequenceMatcher penalises length differences, so `"milk"` vs `"Woolworths Full Cream Milk 2L"` scored below 0.3 even when clearly relevant. Subset boost fixes multi-word and short-name cases.

**History:** Original threshold was 0.3; lowered to 0.15 as a safety net after subset boost was added. Generic path used 0.4 briefly (too strict, Woolworths asymmetry); now **0.25**.

---

### Unit price normalisation for fair comparison

**Decision:** When both products have parseable sizes (e.g. `2L` vs `1L`), compare **per 100ml / per 100g** unit prices for winner and saving. Fall back to pack price when sizes are not normalisable.

**Why:** Comparing a 2L pack to a 1L pack on pack price alone is misleading. Saving uses the same basis as the winner (unit delta or pack delta).

---

### Strict brand filter for branded searches

**Decision:** If no API result contains the queried brand word, return `None` for that store rather than picking a substitute.

**Why:** User searching `"a2 milk"` expects a2, not homebrand milk. Produces `no_comparison` with an explicit note.

---

## Comparison and pricing logic

### Basket winner uses sum of pack prices

**Decision:** Overall winner sums pack prices for items where both stores matched. Tie if totals within **$0.50**; savings set to 0 on tie.

**Why:** Simple, explainable totals for the hero banner. Not an optimised "shop only at winner store" basket.

---

### Annualised savings = weekly savings × 52

**Decision:** `annualised_savings = savings * 52`.

**Why:** Product brief emphasises the yearly household impact to make switching feel worthwhile.

---

### Per-item tie threshold

**Decision:** Item-level tie if prices within 1 cent or 2% relative.

**Why:** Avoid calling a winner on noise from floating point or trivial differences.

---

## Frontend

### Design system from Open Home Loans references

**Decision:** Style the UI from `frontend/frontend_design_references/` PNGs (colours, typography, spacing, components), not ad hoc Tailwind defaults.

**Why:** Assessment is for Open Home Loans; visual consistency with their design language signals craft. Dark theme, accent `#F2A233`, surface tokens defined in Tailwind v4 `@theme`.

---

### Typography: Neue Haas Grotesk Display Pro + DM Mono

**Decision:**

- **Headings and body:** `'Neue Haas Grotesk Display Pro'` via cdnfonts (with system fallbacks).
- **Prices, unit prices, and numeric values:** `'DM Mono'` via Google Fonts (`.font-numeric` class).

**Why:** Matches the style guide. Monospace on currency improves scanability in the results table.

---

### Store logos in results UI

**Decision:** Show Woolworths and Coles logos in the winner column and hero via [`StoreBadge.jsx`](frontend/src/components/StoreBadge.jsx), loading official SVG assets from [`frontend/src/assets/brands/`](frontend/src/assets/brands/) (`woolworths.svg`, `coles.svg`).

**Why:** Clearer than letter badges. Woolworths uses the green apple icon; Coles uses the red wordmark.

---

### Vite proxy targets `127.0.0.1:8000` not `localhost:8000`

**Decision:** Changed proxy target from `http://localhost:8000` to `http://127.0.0.1:8000`.

**Why:** On Windows, `localhost` can resolve to IPv6 (`[::1]`) and hit a different process on port 8000, returning **501 Unsupported method ('POST')**. FastAPI listens on `127.0.0.1`. CORS updated to allow both `localhost:5173` and `127.0.0.1:5173`.

---

### JSDoc types instead of TypeScript

**Decision:** Keep `.jsx` files; mirror API shapes in `frontend/src/lib/types.js` with `@typedef`.

**Why:** Scaffold was JavaScript. JSDoc gives type hints without a migration cost for a small frontend.

---

### Error handling via dedicated `error` view

**Decision:** Failed compare calls set `view='error'` with a notification-style banner and "Try again" (preserves list items). Receipt errors show inline in `ReceiptUpload`.

**Why:** Compare failures are blocking; receipt failures are local to the upload tab.

---

## Testing

### Backend unit tests with mocked APIs

**Decision:** `test_compare.py` mocks Woolworths/Coles search; `test_matching.py` tests pure matching helpers.

**Why:** Compare tests must not hit live RapidAPI. Matching tests run fast without network.

---

## How to use this file

When making a choice that affects behaviour, UX, or architecture:

1. Add a dated subsection under the relevant heading (or create a new heading).
2. State **Decision**, **Why**, and any **Problem / fix / follow-up**.
3. Link to code or docs where helpful.

Do not use em dashes in this file (project convention).
