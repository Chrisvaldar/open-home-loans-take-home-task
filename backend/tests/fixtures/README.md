# Receipt test fixtures (local only)

Place your test receipt image here as `test_receipt.jpg`. This folder is gitignored so personal receipts are never pushed.

## Quick test (recommended)

From the `backend/` directory:

```bash
python scripts/test_receipt.py
```

Calls Gemini directly — no browser, no Swagger, no base64 copy-paste.

## Optional: generate JSON for curl

```bash
python scripts/encode_receipt_fixture.py
```

Writes `receipt_request.json` here (also gitignored). Use with curl:

```bash
curl -X POST http://localhost:8000/api/receipt -H "Content-Type: application/json" -d @tests/fixtures/receipt_request.json
```

Do **not** paste large base64 strings into Swagger `/docs` — browsers often show "Failed to fetch" on huge request bodies.
