# Frugl

A grocery price comparison web app that helps Australian households decide whether to shop at **Coles** or **Woolworths** this week. Enter your regular shopping list, compare current prices and specials, and see how much you could save.

**Live app:** [https://open-home-loans-take-home-task.vercel.app/](https://open-home-loans-take-home-task.vercel.app/)

Built as part of the Open Home Loans take-home assessment (Brief 3A).

## Stack

- **Frontend:** React (Vite) + Tailwind CSS
- **Backend:** FastAPI (Python)
- **Data:** Woolworths & Coles product search via [RapidAPI](https://rapidapi.com/) (data-holdings-group)

## Project structure

```
backend/
  main.py                 # FastAPI app + CORS
  routers/compare.py      # POST /api/compare
  routers/receipt.py      # POST /api/receipt
  tests/fixtures/         # local test receipt images (gitignored)
  scripts/                # receipt test helpers
  services/               # API clients, matching, comparison logic
  tests/                  # pytest unit tests
frontend/
  src/components/         # UI placeholders
  src/lib/api.js          # API client helpers
```

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+
- API keys (see [Environment variables](#environment-variables))

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your keys

uvicorn main:app --reload
```

API runs at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

**Receipt testing:** put a sample image at `backend/tests/fixtures/test_receipt.jpg` (gitignored), then run `python scripts/test_receipt.py` from `backend/`. See [backend/docs/receipt_testing.md](backend/docs/receipt_testing.md) — Swagger often fails on large base64 payloads.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`. Vite proxies `/api` requests to the backend.

### Run tests

```bash
cd backend
pytest
```

Seven compare-basket tests are marked `skip` until comparison logic is implemented. Matching tests and the empty-basket test run now.

## Environment variables

Create `backend/.env` from `backend/.env.example`:

| Variable | Description |
|----------|-------------|
| `RAPIDAPI_KEY` | RapidAPI key for Woolworths & Coles product search |
| `GEMINI_API_KEY` | Google Gemini API key for receipt image extraction |

Never commit `.env` — it is listed in `.gitignore`.

## What's next

- [ ] Live Coles API integration
- [ ] Expanded brand list
- [ ] Loyalty card points integration (Everyday Rewards, Flybuys)
- [ ] Push notifications for weekly specials
- [ ] Store location filtering

## License

Take-home assessment submission — not for production use without review.
