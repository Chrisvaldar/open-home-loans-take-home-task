import os
import re

from groq import Groq

RERANK_MODEL = "llama-3.1-8b-instant"


def _format_candidate(index: int, item: dict) -> str:
    return (
        f"{index}: {item.get('name', '')} | {item.get('brand', '')} | "
        f"{item.get('size', '')} | ${item.get('price', '')}"
    )


def rerank_with_groq(query: str, candidates: list[dict]) -> dict | None:
    """Pick the best API candidate for a receipt line, or None if no good match."""
    print(f"[rerank_with_groq] called query={query!r} candidates={len(candidates)}")
    for index, item in enumerate(candidates):
        print(f"[rerank_with_groq]   {_format_candidate(index, item)}")

    if not candidates:
        print("[rerank_with_groq] skipping — no candidates")
        return None

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[rerank_with_groq] skipping — GROQ_API_KEY not set")
        return None

    candidate_lines = "\n".join(
        _format_candidate(index, item) for index, item in enumerate(candidates)
    )
    max_index = len(candidates) - 1

    prompt = (
        "You are a strict grocery product matcher for Australian supermarket receipts.\n"
        "Your job is to REJECT bad matches. Only accept a candidate when it is clearly "
        "the same product as the receipt line.\n"
        "When in doubt, return -1.\n\n"
        "Return -1 unless ALL of these are true for one candidate:\n"
        "1. Same product TYPE (peas not onion rings, beef mince not pies or dog food, "
        "dishwashing tablets not denture tablets or medicine, brioche bagels not blueberry bagels, "
        "fresh tomatoes not soup or arancini).\n"
        "2. Same or very similar BRAND when the receipt names a brand "
        "(Somat, McCain, Abe's, etc.). Different brand = -1.\n"
        "3. Same or very similar SIZE/weight when the receipt includes one "
        "(500g not 2kg, 360g not 300g unless clearly the same pack). Large size mismatch = -1.\n"
        "4. The product name describes the same item, not just one shared word "
        "(shared word 'beef', 'frozen', 'tablets', or '4' alone is NOT enough).\n\n"
        "Always return -1 for:\n"
        "- Pet food, beer, medicine, denture products, tanning products, unrelated categories\n"
        "- Different flavour or variant (brioche vs blueberry, supergrain vs brioche)\n"
        "- Store name on receipt (COLES/WOOLWORTHS) does NOT mean match any Coles/Woolworths product\n"
        "- Only vague or partial overlap\n"
        "- You would not confidently buy this candidate based on the receipt line\n\n"
        "Produce exception: If the query is a fresh produce item (fruit, vegetable, meat) "
        "and a candidate matches the core ingredient name even if word order differs or "
        "it is sold by each or kg, prefer that over returning -1. "
        "Example: query brown onions → accept Onion Brown each $0.63\n\n"
        f"Return ONLY a single integer: index 0-{max_index} for ONE clear match, "
        "or -1 if no candidate is a clear match.\n"
        "No explanation, just the number.\n"
        f"Receipt item: {query}\n"
        f"Candidates:\n{candidate_lines}"
    )

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=RERANK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict product matcher. Default to -1. "
                        "Only output a valid index when the match is obvious."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        text = (response.choices[0].message.content or "").strip()
        print(f"[rerank_with_groq] raw Groq response={text!r}")
        match = re.search(r"-?\d+", text)
        if not match:
            print("[rerank_with_groq] no integer found in response")
            return None

        index = int(match.group())
        print(f"[rerank_with_groq] parsed index={index}")
        if index == -1:
            print("[rerank_with_groq] Groq rejected all candidates")
            return None
        if 0 <= index < len(candidates):
            selected = candidates[index]
            print(
                "[rerank_with_groq] selected "
                f"{_format_candidate(index, selected)}"
            )
            return selected
        print(f"[rerank_with_groq] index out of range: {index}")
    except Exception as exc:
        print(f"[rerank_with_groq] error={exc!r}")
        return None

    return None
