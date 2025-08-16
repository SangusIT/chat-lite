from pydantic import BaseModel

class Chat(BaseModel):
    username: str
    texts: list