import httpx
from settings import settings

MYMEMORY_URL = "https://api.mymemory.translated.net/get"

async def translate_text(text: str, source: str = "en", target: str = "ru") -> str | None:
    if settings.translate_api_url:
        return await _translate_libre(text, source, target)
    return await _translate_mymemory(text, source, target)

async def _translate_mymemory(text: str, source: str, target: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                MYMEMORY_URL,
                params={"q": text, "langpair": f"{source}|{target}"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("responseData", {}).get("translatedText")
    except Exception:
        return None

async def _translate_libre(text: str, source: str, target: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                settings.translate_api_url,
                json={"q": text, "source": source, "target": target, "format": "text"},
            )
            resp.raise_for_status()
            return resp.json().get("translatedText")
    except Exception:
        return None
