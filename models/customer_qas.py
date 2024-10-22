from datetime import datetime
from typing import Optional, List

from colorama import AnsiToWin32
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field, JSON, Column

from models.answers import Answer
from models.events import Event


class CustomerQA(BaseModel):
    id: int = Field(primary_key=True, default=None)
    writer: str
    email: EmailStr
    password: str
    title: str
    content: str
    attachment: UploadFile
    c_date: datetime
    done: bool
    read_cnt: int
    events: Optional[Answer] = None

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'ex.example.com',
                'events': [],
            }
        }


class UserSingIn(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'ex.example.com',
                'password': '<PASSWORD>',
            }
        }
