from datetime import datetime
from typing import Optional, List

from fastapi import UploadFile
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field, JSON, Column

from models.events import Event


class Answer(BaseModel):
    id: int = Field(primary_key=True, default=None)
    content: str
    customer_qa_id: int

    class Config:
        json_schema_extra = {
            'example': {
                'content': 'example content',
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
