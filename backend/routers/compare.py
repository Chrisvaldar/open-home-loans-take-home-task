from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.compare import compare_basket

router = APIRouter()


class CompareRequest(BaseModel):
    items: list[str]
    receipt_text: Optional[str] = None


@router.post("/compare")
def compare(request: CompareRequest):
    try:
        return compare_basket(request.items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
