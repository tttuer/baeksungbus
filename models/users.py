from pydantic import BaseModel
from sqlalchemy import table
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = 'user'
    id: str = Field(primary_key=True, default=None)
    password: str

    class Config:
        json_schema_extra = {
            'example': {
                'id': 'id',
                'password': 'password',
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str