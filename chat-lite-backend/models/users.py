from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str


class UserAdd(User):
    key: str


class UserPrivate(User):
    hashed_password: str