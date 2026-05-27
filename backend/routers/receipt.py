from fastapi import APIRouter, HTTPException
from google.genai.errors import ServerError
from pydantic import BaseModel

from services.receipt import extract_items_from_receipt

router = APIRouter()


class ReceiptRequest(BaseModel):
    image: str
    mime_type: str = "image/jpeg"


@router.post("/receipt")
def scan_receipt(request: ReceiptRequest):
    try:
        result = extract_items_from_receipt(request.image, request.mime_type)
        return {"items": result}
    except ServerError as exc:
        if exc.code == 503:
            raise HTTPException(
                status_code=503,
                detail="Receipt scanner is busy. Please try again in a moment.",
            ) from exc
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
