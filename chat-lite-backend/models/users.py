from pydantic import BaseModel, EmailStr, SecretStr, model_validator
from typing import Optional

class User(BaseModel):
    username: str
    email: EmailStr

class UserAdd(User):
    user_id: Optional[int] = None
    key: str

class UserPublic(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    user_id: Optional[int] = None

class UserDB(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    user_id: Optional[int] = None

    @model_validator(mode='after')
    def check_at_least_one_field_set(self):
        fields = {k: v for k, v in self.model_dump().items() if v != None}
        if fields == {}:
            raise ValueError("At least one field must be provided.")
        return fields

class UserRegister(BaseModel):
    password: SecretStr
    key: str

class UserPrivate(BaseModel):
    user_id: int
    hashed_password: str