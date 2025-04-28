# app/api/routers/agent.py
from fastapi import APIRouter, HTTPException

from ...services.agent import ChatRequest, chat

router = APIRouter()


@router.post("/chat")
def chat_route(payload: ChatRequest) -> dict[str, str]:
    """
    Conversational endpoint.

    Body:
    {
      "session_id": "...",
      "message": "What's my schedule tomorrow?"
    }
    """
    try:
        reply = chat(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"reply": reply}
