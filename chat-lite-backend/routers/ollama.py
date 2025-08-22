from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from utils.dependencies import verify_server_ip
from utils.funcs import get_list, get_pulled, get_details, get_all

router = APIRouter()

@router.get("/list_available", dependencies=[Depends(verify_server_ip)])
async def list_available(request: Request):
    available = await get_list()
    return available

@router.get("/list_pulled", dependencies=[Depends(verify_server_ip)])
async def list_pulled(request: Request):
    pulled = await get_pulled()
    return pulled

@router.get("/llm_details", dependencies=[Depends(verify_server_ip)])
async def llm_details(llm: str, request: Request):
    details = await get_details(llm)
    return HTMLResponse(details)

@router.get("/all_info", dependencies=[Depends(verify_server_ip)])
async def all_info(request: Request):
    details = await get_all()
    return details