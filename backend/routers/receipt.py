from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ReceiptRequest(BaseModel):
    image: str


@router.post("/receipt")
def scan_receipt(request: ReceiptRequest):
    return {"message": "not implemented", "items": []}
