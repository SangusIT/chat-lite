from fastapi import APIRouter

router = APIRouter(prefix='/chats', tags=['chats'])

@router.get('/')
async def get_chats():
    return [{"name":"chat 1"},{"name":"chat 2"},{"name":"chat 3"}]