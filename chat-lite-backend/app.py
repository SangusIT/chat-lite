from fastapi import FastAPI, WebSocket, Depends, status
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from openai import AsyncOpenAI
from pymongo import AsyncMongoClient
import logging
from dotenv import load_dotenv
import os
import asyncpg
from .routers import admin, users, chats, texts, tokens
from .utils.dependencies import get_current_active_user, verify_key

load_dotenv()

MONGO_USER: str = os.environ.get("MONGO_USER")
MONGO_PASSWORD: str = os.environ.get("MONGO_PASSWORD")
MONGO_HOST: str = os.environ.get("MONGO_HOST")
MONGO_PORT: int = int(os.environ.get("MONGO_PORT"))
PSQL_USER: str = os.environ.get("PSQL_USER")
PSQL_PASSWORD: str = os.environ.get("PSQL_PASSWORD")
PSQL_HOST: str = os.environ.get("PSQL_HOST")
PSQL_DB: str = os.environ.get("PSQL_DB")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ollama_client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    mongo_conn = AsyncMongoClient(host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USER, password=MONGO_PASSWORD)
    psql_conn = await asyncpg.connect(user=PSQL_USER, password=PSQL_PASSWORD, database=PSQL_DB, host=PSQL_HOST)
    logger = logging.getLogger('uvicorn.error')
    app.state.logger = logger
    if ollama_client:
        logger.info('Ollama client loaded.')
        app.state.ollama_client = ollama_client
    if mongo_conn:
        logger.info('MongoDB connected.')
        app.state.mongo_conn = mongo_conn
    if psql_conn:
        logger.info('PostgreSQL connected.')
        app.state.psql_conn = psql_conn
    yield
    await psql_conn.close()
    await mongo_conn.close()

app = FastAPI(lifespan=lifespan)

# app.include_router(tokens.router, dependencies=[Depends(verify_key)])
app.include_router(admin.router, prefix='/admin', tags=['admin'])
app.include_router(users.router, prefix='/users', tags=['users'])

# app.include_router(chats.router, dependencies=[Depends(get_current_active_user)])
# app.include_router(texts.router, dependencies=[Depends(get_current_active_user)])