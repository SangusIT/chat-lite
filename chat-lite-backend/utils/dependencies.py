from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status, Header
from jwt.exceptions import InvalidTokenError
import jwt
import os
from dotenv import load_dotenv
from ..models.users import User, UserPrivate
from ..models.tokens import TokenData
from ..utils.psql import get_user, check_key
from fastapi import Request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

load_dotenv()

X_TOKEN: str = os.environ.get("X_TOKEN")
SECRET_KEY: str = os.environ.get("SECRET_KEY")
ALGORITHM: str = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], conn):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(conn, username=token_data.username)
    user = UserPrivate(**user)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != X_TOKEN:
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    

async def verify_key(key: str, request: Request):
    # user_key = await check_key(psql_conn, key)
    # print('checking request')
    # request = get_database(request)
    # print('request')
    # print(request.app.state.psql_conn)
    if not key == 'user_key':
        raise HTTPException(status_code=400, detail="Invalid key provided.")