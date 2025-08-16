from fastapi import APIRouter

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/')
async def get_users():
    return [{"name":"user 1"},{"name":"user 2"},{"name":"user 3"}]