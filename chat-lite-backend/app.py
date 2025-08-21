from fastapi import FastAPI, WebSocket, Depends, status, Request, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from openai import AsyncOpenAI
from pymongo import AsyncMongoClient
import logging
from dotenv import load_dotenv
import os
import asyncpg
from routers import admin, users, chats, texts, ollama
from utils.funcs import ollama_bot, logger
from utils.dependencies import verify_token, get_current_active_user
from fastapi.middleware.cors import CORSMiddleware
import webbrowser

load_dotenv()

MONGO_USER: str = os.environ.get("MONGO_USER")
MONGO_PASSWORD: str = os.environ.get("MONGO_PASSWORD")
MONGO_HOST: str = os.environ.get("MONGO_HOST")
MONGO_PORT: int = int(os.environ.get("MONGO_PORT"))
OLLAMA_URL: str = os.environ.get("OLLAMA_URL")
PSQL_USER: str = os.environ.get("PSQL_USER")
PSQL_PASSWORD: str = os.environ.get("PSQL_PASSWORD")
PSQL_HOST: str = os.environ.get("PSQL_HOST")
PSQL_DB: str = os.environ.get("PSQL_DB")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ollama_client = AsyncOpenAI(base_url=OLLAMA_URL, api_key="ollama") # need to do all the other checks for ollama from admin dashboard
    mongo_conn = AsyncMongoClient(host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USER, password=MONGO_PASSWORD)
    psql_conn = await asyncpg.connect(user=PSQL_USER, password=PSQL_PASSWORD, database=PSQL_DB, host=PSQL_HOST)
    if ollama_client:
        logger.info('Ollama client loaded.')
        app.state.ollama_client = ollama_client
    if mongo_conn:
        logger.info('MongoDB connected.')
        app.state.mongo_conn = mongo_conn
    if psql_conn:
        logger.info('PostgreSQL connected.')
        app.state.psql_conn = psql_conn
    # webbrowser.open('http://localhost:8000/admin/dashboard', new=2)
    yield
    await psql_conn.close()
    await mongo_conn.close()

app = FastAPI(lifespan=lifespan)

app.include_router(admin.router, prefix='/admin', tags=['admin'])
app.include_router(ollama.router, prefix='/ollama', tags=['ollama'])
app.include_router(users.router, prefix='/users', tags=['users'])
app.include_router(chats.router, prefix='/chats', tags=['chats'], dependencies=[Depends(get_current_active_user)])
app.include_router(texts.router, prefix='/texts', tags=['texts'], dependencies=[Depends(get_current_active_user)])

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)