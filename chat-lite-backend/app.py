from fastapi import FastAPI, WebSocket, Depends
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from openai import AsyncOpenAI
from pymongo import AsyncMongoClient
import logging
import markdown
from dotenv import load_dotenv
import os
import asyncpg
from .routers import users, chats, texts, tokens
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
    global ai_client, mongo_client, psql_client, logger
    ai_client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    mongo_client = AsyncMongoClient(host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USER, password=MONGO_PASSWORD)
    psql_client = await asyncpg.connect(user=PSQL_USER, password=PSQL_PASSWORD, database=PSQL_DB, host=PSQL_HOST)
    logger = logging.getLogger('uvicorn.error')
    logger.info('Ollama client loaded.')
    yield
    await psql_client.close()
    await mongo_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(tokens.router, dependencies=[Depends(verify_key)])
app.include_router(users.router)
app.include_router(chats.router, dependencies=[Depends(get_current_active_user)])
app.include_router(texts.router, dependencies=[Depends(get_current_active_user)])

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

"""
completion(model='ollama/llama3', messages, api_base="http://localhost:11434", stream=False)
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        logger.info('Asking Ollama AI: %s' % data)
        response = await ai_client.chat.completions.create(
            model="llama3",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": data}
            ]
        )
        
        logger.info(response.choices[0].message.content)
        answer = markdown.markdown(response.choices[0].message.content)
        await websocket.send_text(answer)


@app.get("/test")
async def test():
    return "hello"
