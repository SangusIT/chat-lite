from fastapi import APIRouter, Response, Depends, status, Request, HTTPException, Query, BackgroundTasks, WebSocket
from fastapi.responses import HTMLResponse
from typing import Annotated
from utils.dependencies import verify_token, verify_server_ip
from utils.psql import create_db, create_table_users, create_table_chats, create_table_texts, table_schema, exec, drop_table, exec_many
from utils.funcs import process_table_create, send_reg, ping_ollama, check_ollama
import uuid
import requests
from datetime import datetime
from models.tables import Table, TableDelete
from models.users import User, UserAdd, UserDB, UserPublic
import aiohttp
import asyncio
import time

router = APIRouter()

@router.get("/dashboard", dependencies=[Depends(verify_server_ip)])
async def dashboard(request: Request):
    return True

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        ollama_status = await check_ollama()
        await websocket.send_json({"ollama_online": ollama_status})

@router.get('/get_user', response_model=UserPublic, dependencies=[Depends(verify_token)])
async def get_user(user: Annotated[UserDB, Query()], request: Request):
    """
    Lookup a user.
    """
    stmt = "SELECT * FROM users WHERE " + " OR ".join(["%s = '%s'" % (k, v) for k,v in user.items()])
    user = await exec(request.app.state.psql_conn, request.app.state.logger, stmt)
    return UserPublic(**user[0])

@router.get('/get_users', response_model=list[UserPublic], status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
async def get_users(request: Request):
    """
    Gets all users.
    """
    result = await exec(request.app.state.psql_conn, request.app.state.logger, "SELECT user_id, username, email FROM users")
    try:
        result = [UserPublic(**r) for r in result]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return result

@router.post('/create_user', status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
async def create_user(user: Annotated[User, Query()], request: Request, background_tasks: BackgroundTasks):
    """
    Create a new user and trigger sending a registration email to the user.
    """
    user = UserAdd(username=user.username, email=user.email, key=uuid.uuid4().hex)
    result = await exec_many(request.app.state.psql_conn, request.app.state.logger, "INSERT INTO users (username, email, key) VALUES ($1, $2, $3) RETURNING username, email, key", [(user.username, user.email, user.key)])
    if result == None:
        result = {"details":"User created."}
        background_tasks.add_task(send_reg, user=user, logger=request.app.state.logger)
    else:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=("Error creating user: %s." % result))
    return result

@router.delete('/delete_user', status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
async def delete_user(user: Annotated[UserDB, Query()], request: Request):
    """
    Delete a user identified by their ID, username or email.
    """
    stmt = "DELETE FROM users WHERE " + " OR ".join(["%s = '%s'" % (k, v) for k,v in user.items()])
    await exec(request.app.state.psql_conn, request.app.state.logger, stmt)
    return {"details": "User record deleted if it existed."}

@router.get('/verify_database', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
async def verify_database(request: Request, response: Response):
    """
    Verifies that the chat-lite database exists or, if not, creates one.
    """
    logger = request.app.state.logger
    logger.info("Verifying database has been created.")
    result = await create_db()
    logger.info(result)
    if result == "DB created.":
        response.status_code = status.HTTP_201_CREATED
    return {"details": result}

@router.get('/tables', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
async def get_tables(request: Request):
    """
    Gets all table schema.
    """
    result = await table_schema(request.app.state.psql_conn, request.app.state.logger)
    return result

@router.get('/create_users_table', status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
async def create_users_table(request: Request, response: Response):
    """
    Create the users table if it does not exist.
    """
    result = await create_table_users(request.app.state.psql_conn, request.app.state.logger)
    result = process_table_create(result, request.app.state.logger, response)
    return {"details": result}

@router.get('/create_chats_table', status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
async def create_chats_table(request: Request, response: Response):
    """
    Create the chats table if it does not exist.
    """
    result = await create_table_chats(request.app.state.psql_conn, request.app.state.logger)
    result = process_table_create(result, request.app.state.logger, response)
    return {"details": result}

@router.get('/create_texts_table', status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
async def create_texts_table(request: Request, response: Response):
    """
    Create the texts table if it does not exist.
    """
    result = await create_table_texts(request.app.state.psql_conn, request.app.state.logger)
    result = process_table_create(result, request.app.state.logger, response)
    return {"details": result}

@router.delete('/tables', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
async def delete_table(table: Annotated[TableDelete, Query()], request: Request, response: Response):
    """
    Deletes a given table.
    """
    result = await drop_table(request.app.state.psql_conn, table.table_name)
    return {"details": result}