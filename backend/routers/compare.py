from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.compare import compare_basket

router = APIRouter()


class CompareRequest(BaseModel):
    items: list[str]
    receipt_text: Optional[str] = None
    source: Optional[str] = "manual"


@router.post("/compare")
def compare(request: CompareRequest):
    try:
        source = request.source or "manual"
        print(f"[compare router] source={source!r} items={len(request.items)}")
        return compare_basket(request.items, source=source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
