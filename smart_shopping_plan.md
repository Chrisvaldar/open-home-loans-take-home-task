# Smart Shopping Destination — Build Plan
## Open Home Loans Take-Home Assessment (Brief 3A)

---

## The Brief (verbatim summary)

**Problem:** The same basket of groceries can vary 10–20% between Coles and Woolworths in any given week due to rotating specials. Most people don't track this and default to habit.

**Why it matters:** A household spending $250/week on groceries could save $1,300–$2,000/year. The blocker is friction, not willingness.

**What to build:** A tool that takes a user's regular shopping list, analyses current specials at Coles and Woolworths, tells the user which store saves them the most money this week, and by how much.

**What they're assessing:**
- Product thinking — did you understand the user problem?
- Design craft — is it clear, simple, and trustworthy?
- Engineering quality — is it robust and production-minded?
- AI-native approach — did you use AI tools effectively?
- End-to-end ownership — problem to shipped

---

## Time Context

**Total time available:** ~1 week  
**Realistic working hours:** ~3–4 evenings (2–3 hrs each), given assessments/uni commitments  
**Submission:** Working feature + 5–10 min walkthrough (written or video) + code repo

---

## Scope Decision

### What you're building
A web app where a user:
1. Builds their regular shopping list
2. Gets a clear recommendation: "Shop at Woolworths this week — save $18.40"
3. Sees a breakdown of which items are on special where
4. Sees their annualised saving if they kept doing this

### What you're NOT building
- User accounts / auth
- Payment integration
- Mobile app (web is fine)
- Full Coles price coverage (Woolworths API is more accessible — Coles is stretch)
- Receipt scanning (too much scope for one week)

### Data strategy
**Try first (Evening 1):** Woolworths internal API via the `woolworths-api` PyPI wrapper or reverse-engineered endpoints from DevTools. One evening budget — if it's working, use it. If it's flaky, move on.

**Fallback (no shame):** Seed a realistic dataset of ~30 common grocery items with realistic weekly specials that rotate. Be upfront in your walkthrough: *"I explored live data via Woolworths' API and got X working, but for demo stability I used a seeded dataset. In production I'd connect a live feed."* This is a mature, honest engineering answer.

---

## Tech Stack

Pick what you know. Suggested:
- **Frontend:** Next.js + Tailwind (or plain React if faster for you)
- **Backend:** Next.js API routes, or a lightweight FastAPI if you prefer Python for the data layer
- **Data:** Woolworths API wrapper (Python) or a JSON seed file
- **Deployment:** Vercel (free, one command deploy — essential for the submission link)

---

## User Flow

```
Landing / Intro screen
│
│  "Tell us what you buy each week"
│
▼
Shopping List Builder
│  - Search for items (e.g. "milk", "chicken breast", "pasta")
│  - Add quantities (optional — default to 1 unit)
│  - See your list build up on screen
│  - CTA: "Compare stores →"
│
▼
Comparison Loading screen (brief — even 1 second feels intentional)
│  "Finding the best prices this week..."
│
▼
Results screen  ← the hero moment
│
│  ┌─────────────────────────────────────┐
│  │  🏆 Shop at Woolworths this week   │
│  │  You'll save $18.40 on your list   │
│  │  That's ~$950/year if you switch   │
│  └─────────────────────────────────────┘
│
│  Item-by-item breakdown:
│  Item          Coles     Woolworths   Winner
│  Full cream milk $2.80   $2.20 ✓      Woolies
│  Chicken breast  $12.00  $13.50       Coles
│  ... etc
│
│  CTA: "Update my list" | "Save this comparison"
│
▼
(Stretch) Share / Save screen
   - Copy a link or screenshot to share with household
```

---

## Build Increments

This is the most important section. Each increment should be a **meaningful commit** with a clear message. This is how you avoid looking like you vibe-coded the whole thing — the git history tells the story of an engineer who thinks before they type.

---

### Increment 1 — Data layer first (Evening 1)
**Goal:** Know what data you have before you build UI around it.

**Tasks:**
- Try the Woolworths API. Install `woolworths-api` or hit endpoints directly via `fetch`/`requests` and log what comes back
- If it works: write a `getSpecials(items)` function that takes a list of item names and returns prices + whether each is on special
- If it doesn't work cleanly: build your seed data as a typed JSON/TS file with ~30 items, realistic prices, and a `isOnSpecial` + `specialPrice` field for each store
- Write a pure function `compareBasket(list, priceData)` → returns `{ winner, totalColes, totalWoolworths, savings, breakdown[] }`
- **Write tests for this function.** Even 3–4 unit tests. This alone separates you from 80% of take-home submissions.

**Commit messages:**
```
feat: add woolworths API integration with item search
feat: add basket comparison logic
test: add unit tests for compareBasket function
```

---

### Increment 2 — Skeleton UI + list builder (Evening 2)
**Goal:** A working (ugly is fine) list builder that hooks into your data layer.

**Tasks:**
- Set up Next.js project + Tailwind, deploy a blank page to Vercel immediately (get the deploy pipeline working early)
- Build the list builder: search input → results dropdown → add to list → see list
- Wire it to your real data (even if the comparison page isn't built yet, the search should return real items)
- State management: keep it simple, `useState` is fine, no need for Redux

**Commit messages:**
```
feat: scaffold Next.js app with Tailwind, deploy to Vercel
feat: item search component with add-to-list functionality
feat: connect item search to price data layer
```

---

### Increment 3 — Results screen (Evening 3)
**Goal:** The hero moment. This is what they'll see in the demo.

**Tasks:**
- Build the results screen: winner banner, savings figure, annualised projection
- Build the item breakdown table
- Make the winner feel obvious at a glance — don't make the user do mental work
- Make the dollar figures feel real: format as `$18.40`, show the annualised figure prominently
- Add a loading state between list builder and results (even a fake 1s delay feels intentional)

**Commit messages:**
```
feat: results screen with winner recommendation and savings summary
feat: item breakdown table with per-item price comparison
feat: annualised savings projection and loading state
```

---

### Increment 4 — Polish + edge cases (Evening 4 / final push)
**Goal:** Make it feel like something you'd actually ship.

**Tasks:**
- Empty states: what happens if someone searches for something not in your dataset?
- Tie: what if both stores cost the same? (rare but handle it)
- Mobile responsiveness — check it on your phone
- Basic error handling — if the API call fails, show something useful
- Write your walkthrough doc / record your video
- Final deploy check — click through the whole flow on the Vercel URL

**Commit messages:**
```
fix: handle empty search results and unknown items gracefully
fix: handle tie-breaker case in comparison logic
style: mobile responsive layout pass
docs: add README with setup instructions and architecture notes
```

---

## Your Walkthrough Script (what to cover)

Structure it around their four criteria so they can tick the boxes easily:

1. **The problem I focused on** — friction of not knowing where to shop, not price-consciousness itself
2. **Key product decisions** — why list-first (not receipt upload), why annualised figure matters, how you handled the data situation
3. **Engineering decisions** — why you separated the comparison logic from the UI, what you'd do differently with more time
4. **What's next** — receipt scanning, real-time API, loyalty card integration (Everyday Rewards vs Flybuys), push notifications on big weekly savings

---

## How to Not Look Like You Vibe-Coded It

The git history is your portfolio. Interviewers *will* look at it.

- **Commit often and with intent.** Each commit should represent one decision, not a dump of everything you did in 3 hours
- **Write a proper README** — setup instructions, architecture overview, known limitations, what you'd do next
- **Add at least a few tests** — even just for the comparison logic. No tests = vibe code
- **Leave intentional TODOs in the code** — `// TODO: replace seed data with live Woolworths API` shows you know what you built and why
- **Don't over-engineer** — a simple thing done well beats a complex thing done messily. Resist adding features in the last hour
- **In the walkthrough, explain tradeoffs** — "I chose X over Y because..." is engineer-brained. "I built X" is not

---

## What to Say About AI Tool Usage

They explicitly want to see AI-native approach, so don't hide it — frame it well:

> "I used Cursor/Claude to accelerate boilerplate (component scaffolding, Tailwind layout) and to explore the Woolworths API structure faster than I could manually. All product decisions, architecture, and logic were mine — I treated AI as a pair programmer, not an author."

That's the right answer. It shows you know how to use the tools without outsourcing your thinking.
