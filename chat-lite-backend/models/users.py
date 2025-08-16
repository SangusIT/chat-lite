from pydantic import BaseModel

class User(BaseModel):
    username: str
    disabled: bool | None = None
    key: str


class UserPrivate(User):
    hashed_password: str