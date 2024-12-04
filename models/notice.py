from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Enum

from models.answers import Answer


# 1. ENUM 정의
class NoticeType(PyEnum):
    TIME = "TIME"
    TTOCK = "TTOCK"
    NOTICE = "NOTICE"


class NoticeBase(SQLModel):
    writer: str = '평택여객(주)'
    email: Optional[EmailStr] = None
    title: str
    content: Optional[str] = None
    attachment: Optional[bytes] = None
    attachment_filename: Optional[str] = None
    c_date: Optional[datetime] = None
    done: bool = False
    read_cnt: int = 0
    notice_type: NoticeType = Field(sa_column=Enum(NoticeType), default=NoticeType.NOTICE)  # qa_type 필드 추가
    creator: Optional[str]


class Notice(NoticeBase, table=True):
    __tablename__ = 'notice'
    id: int = Field(primary_key=True, default=None)

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'title',
                'notice_type': 'NOTICE',
            }
        }


class NoticeShort(SQLModel):
    id: int
    title: str
    writer: str
    c_date: str
    done: bool
    read_cnt: int
    attachment_filename: Optional[str]
    notice_type: NoticeType

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


class NoticePublic(NoticeBase):
    id: int


class NoticeWithAnswer(NoticePublic):
    answers: list[Answer] = []


class NoticeUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    attachment: Optional[bytes] = None
