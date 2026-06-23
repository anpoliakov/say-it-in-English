from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from models import User
from auth import get_current_user
from translate import translate_text

router = APIRouter(prefix="/translate", tags=["translate"])

class TranslationOut(BaseModel):
    translation: str | None

@router.get("", response_model=TranslationOut)
async def translate(
    text: str = Query(..., min_length=1, max_length=500),
    source: str = Query("en"),
    target: str = Query("ru"),
    user: User = Depends(get_current_user),
):
    result = await translate_text(text, source, target)
    return TranslationOut(translation=result)
