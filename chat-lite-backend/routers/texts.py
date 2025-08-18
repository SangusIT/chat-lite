from fastapi import APIRouter

router = APIRouter()

@router.get('/')
async def get_texts():
    return [{"name":"text 1"},{"name":"text 2"},{"name":"text 3"}]