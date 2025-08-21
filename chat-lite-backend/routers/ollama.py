from fastapi import APIRouter, Response, Depends, status, Request, HTTPException, Query, BackgroundTasks, WebSocket
from fastapi.responses import HTMLResponse
from typing import Annotated
from utils.dependencies import verify_token, verify_server_ip
from utils.psql import create_db, create_table_users, create_table_chats, create_table_texts, table_schema, exec, drop_table, exec_many
from utils.funcs import process_table_create, send_reg, ping_ollama, check_ollama, logger, get_list, get_pulled, get_details
import uuid
import requests
from datetime import datetime
from models.tables import Table, TableDelete
from models.users import User, UserAdd, UserDB, UserPublic
import aiohttp
import asyncio
import time

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