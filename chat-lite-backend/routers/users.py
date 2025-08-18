from fastapi import APIRouter, Request, Depends, status, Query, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
from pydantic import SecretStr
from fastapi.responses import HTMLResponse
from utils.dependencies import verify_key, get_current_active_user
from models.users import User, UserPublic, UserDB
from models.tokens import Token
from utils.psql import exec, get_user
from utils.funcs import authenticate_user, create_access_token
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

@router.post('/register', dependencies=[Depends(verify_key)])
async def register_account(request: Request, current_user: Annotated[User, Depends(verify_key)]):
    """
    Complete user registration by adding a password.
    """
    stmt = "UPDATE users SET hashed_password = '%s', key = '' WHERE user_id = %s" % (current_user.hashed_password, current_user.user_id)
    await exec(request.app.state.psql_conn, request.app.state.logger, stmt)
    user = await get_user(request.app.state.psql_conn, 'user_id', current_user.user_id, request.app.state.logger)
    return {"details": "Password set.", 'user': UserPublic(**user[0])}

@router.post("/token")
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request):
    user = await authenticate_user(form_data.username, form_data.password, request.app.state.psql_conn, request.app.state.logger)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get('/get_user', response_model=UserPublic, dependencies=[Depends(get_current_active_user)])
async def get_user(user: Annotated[UserDB, Depends(get_current_active_user)], request: Request):
    """
    Lookup a user.
    """
    request.app.state.logger.info(user)
    stmt = "SELECT * FROM users WHERE user_id = %s" % user.user_id
    user = await exec(request.app.state.psql_conn, request.app.state.logger, stmt)
    return UserPublic(**user[0])