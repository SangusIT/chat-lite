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


async def authenticate_user(username: str, password: str, conn, logger):
    user = await get_user(conn, 'username', username, logger)
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