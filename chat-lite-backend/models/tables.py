from pydantic import BaseModel

class Table(BaseModel):
    table_name: str
    is_insertable_into: str

class TableDelete(BaseModel):
    model_config = {"extra": "forbid"}
    table_name: str