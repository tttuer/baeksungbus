from pydantic import BaseModel
from sqlmodel import SQLModel


class User(SQLModel):
    id: str
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