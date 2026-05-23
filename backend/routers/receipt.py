from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.receipt import extract_items_from_receipt

router = APIRouter()


class ReceiptRequest(BaseModel):
    image: str


@router.post("/receipt")
def scan_receipt(request: ReceiptRequest):
    try:
        result = extract_items_from_receipt(request.image)
        return {"items": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
