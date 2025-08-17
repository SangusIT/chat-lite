from fastapi import APIRouter, Response, Depends, status, Request, HTTPException, Query
from typing import Annotated
from ..utils.dependencies import verify_token
from ..utils.psql import create_db, create_table_users, create_table_chats, create_table_texts, table_schema, exec, drop_table
import json
import uuid
from dotenv import load_dotenv
from asyncpg.exceptions import UndefinedTableError
from ..models.tables import Table, TableDelete
from ..models.users import User, UserAdd



router = APIRouter()

@router.post('/create_user', dependencies=[Depends(verify_token)], status_code=status.HTTP_201_CREATED)
async def create_user(user: User, request: Request, response: Response):
    """
    Create a new user and trigger sending a registration email to the user.
    """
    user = UserAdd(username=user.username, email=user.email, key=uuid.uuid4().hex)
    stmt = f"INSERT INTO users (username, email, key) VALUES ($1, $2, $3) RETURNING username, email, key;",
    args = [(user.username, user.email, user.key)]
    logger = request.app.state.logger
    logger.info(stmt)
    logger.info(args)
    result = await exec(request.app.state.psql_conn, request.app.state.logger, stmt, args)
    if result:
        {"details":"User created."}
    else:
        {"details":"Error creating user."}
    return result

@router.get('/verify_database', dependencies=[Depends(verify_token)], status_code=status.HTTP_200_OK)
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

@router.get('/tables', response_model=list[Table], dependencies=[Depends(verify_token)], status_code=status.HTTP_200_OK)
async def get_tables(request: Request, response: Response):
    """
    Gets all table schema.
    """
    result = await table_schema(request.app.state.psql_conn, request.app.state.logger)
    if result != []:
        result = [Table(res) for res in result]
    return result

@router.get('/create_users_table', dependencies=[Depends(verify_token)], status_code=status.HTTP_201_CREATED)
async def create_users_table(request: Request, response: Response):
    """
    Create the users table if it does not exist.
    """
    logger = request.app.state.logger
    logger.info("Creating users table.")
    result = await create_table_users(request.app.state.psql_conn, request.app.state.logger)
    logger.info(result)
    if not result:
        result = "Table previously created." 
        response.status_code = status.HTTP_200_OK
    else:
        result = "Users table created."
    return {"details": result}

@router.get('/create_chats_table', dependencies=[Depends(verify_token)], status_code=status.HTTP_201_CREATED)
async def create_chats_table(request: Request, response: Response):
    """
    Create the chats table if it does not exist.
    """
    logger = request.app.state.logger
    logger.info("Creating chats table.")
    result = await create_table_chats(request.app.state.psql_conn, request.app.state.logger)
    logger.info(result)
    if not result:
        result = "Table previously created." 
        response.status_code = status.HTTP_200_OK
    else:
        result = "Chats table created."
    return {"details": result}

@router.get('/create_texts_table', dependencies=[Depends(verify_token)], status_code=status.HTTP_201_CREATED)
async def create_texts_table(request: Request, response: Response):
    """
    Create the texts table if it does not exist.
    """
    logger = request.app.state.logger
    logger.info("Creating texts table.")
    result = await create_table_texts(request.app.state.psql_conn, request.app.state.logger)
    logger.info(result)
    if not result:
        result = "Table previously created." 
        response.status_code = status.HTTP_200_OK
    else:
        result = "Texts table created."
    return {"details": result}

@router.delete('/tables', dependencies=[Depends(verify_token)], status_code=status.HTTP_200_OK)
async def delete_table(table: Annotated[TableDelete, Query()], request: Request, response: Response):
    """
    Deletes a given table.
    """
    result = await drop_table(request.app.state.psql_conn, table.table_name)
    return {"details": result}