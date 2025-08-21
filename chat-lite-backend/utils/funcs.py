from datetime import datetime, timedelta, timezone
from fastapi import status, HTTPException
import os
import jwt
from dotenv import load_dotenv
from models.users import UserPrivate, UserPublic
from utils.psql import get_user
from passlib.context import CryptContext
import markdown
import boto3
from models.users import User
import aiohttp
import asyncio
import logging
import requests
from bs4 import BeautifulSoup
import subprocess
import pandas as pd

logger = logging.getLogger('uvicorn.error')

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
EMAILER: str = os.environ.get("EMAILER")
SECRET_KEY: str = os.environ.get("SECRET_KEY")
ALGORITHM: str = os.environ.get("ALGORITHM")
ACCESS_KEY: str = os.environ.get("ACCESS_KEY")
SECRET_ACCESS_KEY: str = os.environ.get("SECRET_ACCESS_KEY")


def process_table_create(result, logger, response):
    logger.info(result)
    if result == 0:
        result = "Table previously created." 
        response.status_code = status.HTTP_200_OK
    elif result == "CREATE TABLE":
        result = "Table created."
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.message)
    return result


def send_reg(user: User, logger):
    logger.info("Sending registration email to: %s" % user.email)
    client = boto3.client(
        'ses',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        region_name='us-east-2'
    )
    result = client.send_email(
        Source=EMAILER,
        Destination={
            'ToAddresses': [
                user.email,
            ]
        },
        Message={
            'Subject': {
                'Data': 'Welcome to Chat-Lite',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': f'Congratulations, you have been invited to try out our chat app. Please follow this link to continue: {('http://localhost:3000/register?key=' + user.key)}',
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': f'Congratulations, you have been invited to try out our chat app. Please follow this link to continue: <a href="{('http://localhost:3000/register?key=' + user.key)}">{('http://localhost:3000/register?key=' + user.key)}</a>',
                    'Charset': 'UTF-8'
                }
            }
        },
        ReplyToAddresses=[
            EMAILER,
        ],
    )
    logger.info(result)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(username: str, password: str, conn):
    user = await get_user(conn, 'username', username)
    user = UserPrivate(**user[0])
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return UserPublic(user_id=user.user_id, username=username)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def ollama_bot(logger, ollama_client, data):
    logger.info('Asking Ollama AI: %s' % data)
    response = await ollama_client.chat.completions.create(
        model="llama3",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": data}
        ]
    )
    logger.info(response.choices[0].message.content)
    answer = markdown.markdown(response.choices[0].message.content)
    return answer


async def ping_ollama(session):
    # logger.info('pinging ollama')
    try:
        async with session.get('http://localhost:11434/') as response:
            await asyncio.sleep(1)
            return True
    except Exception as e:
        return False
    
async def check_ollama():    
    async with aiohttp.ClientSession() as session:
        result = await asyncio.gather(ping_ollama(session))
        return result[0]

async def ollama_ps():
    running = os.system("ollama ps")
    return running

async def get_pulled():
    output = subprocess.check_output("ollama ls", shell=True, text=True)
    output = output.split("\n")
    output = [o.split("    ") for o in output[1:-1]]
    cleaned = [[c.strip() for c in o] for o in output]
    df = pd.DataFrame([o[:4] for o in cleaned], columns=["name", "id", "size", "last modified"])
    return df.to_dict("records")

async def get_list():
    r = requests.get("https://ollama.com/library")
    soup = BeautifulSoup(r.text)
    available = soup.find_all("span", "group-hover:underline truncate")
    return [a.get_text() for a in available]

async def get_details(llm):
    r = requests.get("https://ollama.com/library/%s" % llm)
    logger.info(dir(r))
    soup = BeautifulSoup(r.text)
    return soup