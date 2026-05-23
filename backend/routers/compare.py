from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CompareRequest(BaseModel):
    items: list[str]
    receipt_text: Optional[str] = None


@router.post("/compare")
def compare(request: CompareRequest):
    return {"message": "not implemented"}
