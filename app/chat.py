import httpx
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

logger = logging.getLogger(__name__)

router = APIRouter()

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = DEFAULT_MODEL
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500


class ChatResponse(BaseModel):
    message: ChatMessage
    done: bool


WINE_SYSTEM_PROMPT = """You are a helpful Wine API assistant. You help users with:
- Wine types, varieties, and regions
- Food pairing suggestions
- Using the Wine API (authentication, rate limits, endpoints)
- Pricing and subscription tiers

Keep responses concise and helpful. If you don't know something, say so.
"""


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with local LLM via Ollama"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            messages = [{"role": "system", "content": WINE_SYSTEM_PROMPT}]
            messages.extend([msg.model_dump() for msg in request.messages])

            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": request.model or DEFAULT_MODEL,
                    "messages": messages,
                    "temperature": request.temperature or 0.7,
                    "stream": False,
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=502, detail=f"Ollama error: {response.text}"
                )

            data = response.json()
            return ChatResponse(
                message=ChatMessage(
                    role=data.get("message", {}).get("role", "assistant"),
                    content=data.get("message", {}).get("content", ""),
                ),
                done=data.get("done", True),
            )

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Ollama. Make sure it's running: `ollama serve`",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, detail="Ollama request timed out. Try a smaller model."
        )
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """List available Ollama models"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                return response.json()
            return {"models": []}
    except httpx.ConnectError:
        return {"models": [], "error": "Ollama not running"}
