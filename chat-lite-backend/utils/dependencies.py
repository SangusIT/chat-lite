from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status, Header, Query
from jwt.exceptions import InvalidTokenError
import jwt
import os
from dotenv import load_dotenv
from models.users import User, UserPrivate, UserRegister
from utils.funcs import get_password_hash
from models.tokens import TokenData
from utils.psql import get_user, check_key
from fastapi import Request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

load_dotenv()

X_TOKEN: str = os.environ.get("X_TOKEN")
SECRET_KEY: str = os.environ.get("SECRET_KEY")
ALGORITHM: str = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"msg":"Could not validate credentials","token_invalid":True},
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
    user = await get_user(request.app.state.psql_conn, 'username', token_data.username, request.app.state.logger)
    user = UserPrivate(**user[0])
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.hashed_password == '':
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != X_TOKEN:
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    

async def verify_key(user: Annotated[UserRegister, Query()], request: Request):
    result = await check_key(request.app.state.psql_conn, user.key,  request.app.state.logger)
    if len(result) == 0:
        raise HTTPException(status_code=400, detail="Invalid key provided or previously registered.")
    request.app.state.logger.info('result')
    request.app.state.logger.info(result[0]['user_id'])
    user = UserPrivate(user_id=result[0]['user_id'], hashed_password=get_password_hash(user.password.get_secret_value()))
    request.app.state.logger.info(result)
    return user