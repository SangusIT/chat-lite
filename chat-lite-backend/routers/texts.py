from fastapi import APIRouter

router = APIRouter(prefix='/texts', tags=['texts'])

@router.get('/')
async def get_chats():
    return [{"name":"text 1"},{"name":"text 2"},{"name":"text 3"}]