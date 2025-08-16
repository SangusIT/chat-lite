from pydantic import BaseModel
from fastapi import UploadFile

class Text(BaseModel):
    content: str
    file: UploadFile