import os
import httpx
import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from slowapi import Limiter
from slowapi.util import get_remote_address
import re

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
if os.environ.get("DOCKER"):
    OLLAMA_BASE_URL = "http://host.docker.internal:11434"

DEFAULT_MODEL = "gemma3:4b"
MAX_INPUT_LENGTH = 2000
MAX_MESSAGES = 20
MAX_TOKENS = 500

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

ALLOWED_MODELS = {
    "gemma3:4b",
    "gemma3:latest",
    "gemma3:1b",
    "qwen3:8b",
    "qwen2.5-coder:3b",
    "qwen2.5-coder:7b",
    "llama3.2",
    "llama3.1",
    "mistral",
    "codellama",
    "phi3",
}


class ChatMessage(BaseModel):
    role: str
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Message content cannot be empty")
        if len(v) > MAX_INPUT_LENGTH:
            raise ValueError(f"Message too long (max {MAX_INPUT_LENGTH} chars)")
        return v.strip()


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = DEFAULT_MODEL
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: List[ChatMessage]) -> List[ChatMessage]:
        if not v:
            raise ValueError("At least one message required")
        if len(v) > MAX_MESSAGES:
            raise ValueError(f"Too many messages (max {MAX_MESSAGES})")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() not in ALLOWED_MODELS:
            raise ValueError(f"Model not allowed. Use: {', '.join(ALLOWED_MODELS)}")
        return v.lower() if v else DEFAULT_MODEL

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> float:
        if v is not None and (v < 0 or v > 2):
            raise ValueError("Temperature must be between 0 and 2")
        return v if v is not None else 0.7

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v: Optional[int]) -> int:
        if v is not None and (v < 1 or v > MAX_TOKENS):
            raise ValueError(f"max_tokens must be between 1 and {MAX_TOKENS}")
        return v if v else MAX_TOKENS


class ChatResponse(BaseModel):
    message: ChatMessage
    done: bool


WINE_SYSTEM_PROMPT = """You are a helpful Wine API assistant. You help users with:
- Wine types, varieties, and regions
- Food pairing suggestions
- Using the Wine API (authentication, rate limits, endpoints)
- Pricing and subscription tiers

Keep responses concise and helpful. If you don't know something, say so.

Important: You should only discuss wine-related topics. Politely redirect if asked about unrelated topics."""


def sanitize_message(content: str) -> str:
    content = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", content)
    content = re.sub(r"https?://[^\s]+", "[link removed]", content)
    if len(content) > 10000:
        content = content[:10000] + "... [truncated]"
    return content


async def verify_api_key(api_key: Optional[str] = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    from app.models import APIKey
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        db_key = (
            db.query(APIKey).filter(APIKey.key == api_key, APIKey.is_active).first()
        )
        if not db_key:
            raise HTTPException(status_code=403, detail="Invalid API key")
        return db_key
    finally:
        db.close()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    api_key: Any = Depends(verify_api_key),
):
    """Chat with local LLM via Ollama (requires API key)"""

    sanitized_messages = [
        ChatMessage(role=msg.role, content=sanitize_message(msg.content))
        for msg in chat_request.messages
    ]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            messages = [{"role": "system", "content": WINE_SYSTEM_PROMPT}]
            messages.extend([msg.model_dump() for msg in sanitized_messages])

            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": chat_request.model or DEFAULT_MODEL,
                    "messages": messages,
                    "temperature": chat_request.temperature or 0.7,
                    "stream": False,
                },
            )

            if response.status_code != 200:
                logger.error(f"Ollama error: {response.text}")
                raise HTTPException(
                    status_code=502, detail="AI service temporarily unavailable"
                )

            data = response.json()
            content = data.get("message", {}).get("content", "")
            content = sanitize_message(content)

            return ChatResponse(
                message=ChatMessage(
                    role=data.get("message", {}).get("role", "assistant"),
                    content=content,
                ),
                done=data.get("done", True),
            )

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable. Please try again later.",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, detail="Request timed out. Please try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/models")
async def list_models():
    """List available Ollama models (internal only)"""
    return {"models": [], "message": "Models managed locally"}
