import base64
from enum import Enum as PyEnum
from typing import Optional

from fastapi import UploadFile, File, Form
from pydantic import EmailStr, BaseModel
from sqlmodel import SQLModel, Field, Enum


# 1. ENUM 정의
class NoticeType(PyEnum):
    TIME = "TIME"
    TTOCK = "TTOCK"
    NOTICE = "NOTICE"


class NoticeBase(SQLModel):
    writer: str = '백성운수(주)'
    email: Optional[EmailStr] = None
    title: str
    content: Optional[str] = None
    attachment: Optional[bytes] = None
    attachment_filename: Optional[str] = None
    c_date: Optional[str] = None
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

    def to_notice_public(self):
        return NoticePublic(
            id=self.id,
            writer=self.writer,
            title=self.title,
            content=self.content,
            attachment=base64.b64encode(self.attachment).decode("cp949") if self.attachment else None,
            attachment_filename=self.attachment_filename,
            c_date=self.c_date,
            read_cnt=self.read_cnt,
            notice_type=self.notice_type,
        )


class NoticeShort(SQLModel):
    num: int
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


class NoticePublic(BaseModel):
    id: int
    title: str
    content: str
    attachment: Optional[str] = None
    attachment_filename: Optional[str] = None
    writer: str = '백성운수(주)'
    c_date: Optional[str]
    read_cnt: int
    notice_type: NoticeType  # qa_type 필드 추가


class NoticeUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    attachment: Optional[bytes] = None


class NoticeRequest(SQLModel):
    title: str
    content: str
    attachment: Optional[UploadFile] = File(None)

    @classmethod
    def as_form(
            cls,
            title: str = Form(...),
            content: str = Form(...),
            attachment: UploadFile = File(None),
    ) -> "NoticeRequest":
        return cls(title=title, content=content, attachment=attachment)

    async def to_notice(self) -> Notice:
        data = self.model_dump()

        if self.attachment:
            data['attachment'] = await self.attachment.read()
            data['attachment_filename'] = self.attachment.filename

        return Notice(**data)
