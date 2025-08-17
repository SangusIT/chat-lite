from datetime import datetime, timedelta, timezone
import os
import jwt
from dotenv import load_dotenv
from ..models.users import UserPrivate
from ..utils.psql import get_user
from passlib.context import CryptContext
import markdown
import boto3
from ..models.users import User


load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
EMAILER: str = os.environ.get("EMAILER")
SECRET_KEY: str = os.environ.get("SECRET_KEY")
ALGORITHM: str = os.environ.get("ALGORITHM")
ACCESS_KEY: str = os.environ.get("ACCESS_KEY")
SECRET_ACCESS_KEY: str = os.environ.get("SECRET_ACCESS_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))


def send_reg(user: User):
    client = boto3.client(
        'ses',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_ACCESS_KEY
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
                    'Data': 'Congratulations, you have been invited to try out our chat app. Please follow this link to continue: http://localhost:8000/%s' % user.key,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': 'Congratulations, you have been invited to try out our chat app. Please follow this link to continue: http://localhost:8000/%s' % user.key,
                    'Charset': 'UTF-8'
                }
            }
        },
        ReplyToAddresses=[
            EMAILER,
        ],
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(username: str, password: str, client):
    user = await get_user(client, username)
    user = UserPrivate(**user)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


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