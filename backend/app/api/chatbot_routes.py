from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.chatbot.agent import ask_chatbot

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    reply: str

@router.post("/ask", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint to communicate with the dynamic LangGraph SQL Agent.
    """
    try:
        logger.info(f"Received chatbot query: {request.message}")
        
        # Convert Pydantic models to dicts for the agent
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        # Invoke the LangGraph agent
        reply = ask_chatbot(request.message, history=history_dicts)
        
        return ChatResponse(reply=reply)
        
    except Exception as e:
        logger.error(f"Chatbot error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")
