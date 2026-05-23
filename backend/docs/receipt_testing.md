# Receipt API testing

## Why Swagger `/docs` shows "Failed to fetch"

The receipt endpoint expects a **full base64-encoded JPEG** in the JSON body. A typical phone photo is 2–4 MB, which becomes ~3–5 MB of base64 text. Swagger UI sends that through the browser's fetch API, which often fails with **"Failed to fetch"** (body too large, timeout, or memory limits).

This is not a backend bug — use one of the methods below instead.

## Fixture location (not in git)

Put your test image at:

```
backend/tests/fixtures/test_receipt.jpg
```

That path is gitignored. See `tests/fixtures/README.md`.

## Recommended: Python script

From `backend/` with `GEMINI_API_KEY` set in `.env`:

```bash
python scripts/test_receipt.py
```

Calls `extract_items_from_receipt` directly — no copy-paste, no browser.

To test through the running server:

```bash
uvicorn main:app --reload
# another terminal:
python scripts/test_receipt.py --http
```

## curl with generated JSON

```bash
python scripts/encode_receipt_fixture.py
curl -X POST http://localhost:8000/api/receipt \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/receipt_request.json
```

`receipt_request.json` is also gitignored.

## Base64 format

Send **raw base64 only** in the `image` field — not a `data:image/jpeg;base64,...` URL (the service strips that prefix if present).

## Do not use browser fetch on local files

HTML or DevTools snippets that do `fetch('test_receipt.jpg')` fail when:

- The page is opened as `file://`
- The path is wrong relative to the page
- CORS blocks reading local files

Use the Python scripts above instead.
