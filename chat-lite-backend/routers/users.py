from fastapi import APIRouter, Response, Depends, status
from ..utils.dependencies import verify_key

router = APIRouter()

@router.post('/', dependencies=[Depends(verify_key)])
async def register_account(response: Response):
    # print('router info')
    # print(router)
    # print(dir(router))
    return [{"name":"user 1"},{"name":"user 2"},{"name":"user 3"}]