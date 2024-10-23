from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field, Relationship

from models.answers import Answer

class CustomerQABase(SQLModel):
    writer: str
    email: Optional[EmailStr] = None
    password: str
    title: str
    content: Optional[str] = None
    attachment: Optional[bytes] = None
    c_date: Optional[datetime] = None
    done: bool = False
    read_cnt: int = 0

class CustomerQA(CustomerQABase, table=True):
    __tablename__ = 'customer_qa'
    id: int = Field(primary_key=True, default=None)

    # Answer와의 1:N 관계 설정
    answers: List[Answer] = Relationship(back_populates="customer_qa")

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'ex.example.com',
                'answers': [],
            }
        }

class CustomerQAShort(SQLModel):
    id: int
    title: str
    writer: str
    c_date: str
    done: bool
    read_cnt: int
    attachment: Optional[bytes] = None

    @property
    def c_date_formatted(self) -> str:
        return self.c_date.strftime('%Y-%m-%d')

    class Config:
        json_schema_extra = {
            'example': {
                'id': 1,
                'title': 'title',
                'writer': 'writer',
                'c_date': '2024-10-23',
                'done': True,
                'read_cnt': 1,
            }
        }

class CustomerQAPublic(CustomerQABase):
    id: int

class CustomerQAWithAnswer(CustomerQAPublic):
    answers: list[Answer] = []