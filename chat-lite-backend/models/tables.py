from pydantic import BaseModel

class Table(BaseModel):
    table_name: str
    column_name: str | None
    data_type: str | None
    character_maximum_length: int | None
    column_default: str | None
    is_nullable: bool | None

class TableDelete(BaseModel):
    table_name: str