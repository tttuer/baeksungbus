from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: str = Field(primary_key=True, default=None)
    password: str

    class Config:
        json_schema_extra = {
            'example': {
                'id': 'id',
                'password': 'password',
            }
        }

    class Settings:
        name = 'users'


class TokenResponse(BaseModel):
    access_token: str
    token_type: str