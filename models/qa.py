from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship, Enum

from models.answers import Answer


# 1. ENUM 정의
class QAType(PyEnum):
    CUSTOMER = "CUSTOMER"
    LOST = "LOST"

class QABase(SQLModel):
    writer: str
    email: Optional[EmailStr] = None
    password: str
    title: str
    content: Optional[str] = None
    attachment: Optional[bytes] = None
    c_date: Optional[datetime] = None
    done: bool = False
    read_cnt: int = 0
    qa_type: QAType = Field(sa_column=Enum(QAType), default=QAType.CUSTOMER)  # qa_type 필드 추가

class QA(QABase, table=True):
    __tablename__ = 'qa'
    id: int = Field(primary_key=True, default=None)

    # Answer와의 1:N 관계 설정
    answers: List[Answer] = Relationship(back_populates="qa", cascade_delete=True)

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'ex.example.com',
                'answers': [],
            }
        }

class QAShort(SQLModel):
    id: int
    title: str
    writer: str
    c_date: str
    done: bool
    read_cnt: int
    attachment: Optional[bytes] = None
    qa_type: QAType = Field(sa_column=Enum(QAType), default=QAType.CUSTOMER)  # qa_type 필드 추가

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

class QAPublic(QABase):
    id: int

class QAWithAnswer(QAPublic):
    answers: list[Answer] = []

class QAUpdate(SQLModel):
    writer: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    content: Optional[str] = None
    attachment: Optional[bytes] = None