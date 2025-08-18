from fastapi import APIRouter, Request, WebSocket, Depends
from typing import Annotated
from fastapi.responses import HTMLResponse
from ..utils.funcs import ollama_bot
from ..utils.dependencies import get_current_active_user

router = APIRouter()

@router.get('/')
async def get_chats(request: Request, dependencies=[Depends(get_current_active_user)]):
    return [{"name":"chat 1"},{"name":"chat 2"},{"name":"chat 3"}]