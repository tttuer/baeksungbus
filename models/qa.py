from enum import Enum as PyEnum
from typing import Optional, List

from pydantic import EmailStr, BaseModel
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
    attachment_filename: Optional[str] = None
    c_date: Optional[str] = None
    done: bool = False
    read_cnt: int = 0
    hidden: bool = False
    qa_type: QAType = Field(sa_column=Enum(QAType), default=QAType.CUSTOMER)  # qa_type 필드 추가

    @property
    def c_date_formatted(self) -> str:
        return self.c_date.strftime('%Y-%m-%d')


class QA(QABase, table=True):
    __tablename__ = 'qa'
    id: int = Field(primary_key=True, default=None)

    # Answer와의 1:N 관계 설정
    answers: List[Answer] = Relationship(back_populates="qa", cascade_delete=True)

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


class QAShort(SQLModel):
    id: int
    title: str
    writer: str
    c_date: str
    done: bool
    read_cnt: int
    attachment: Optional[bytes] = None
    hidden: bool
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
    attachment: Optional[str] = None  # Base64 인코딩된 문자열로 변환


class QAWithAnswer(QAPublic):
    answers: Optional[list[Answer]] = []


class QAUpdate(SQLModel):
    writer: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    content: Optional[str] = None
    attachment: Optional[bytes] = None
    hidden: Optional[bool] = None


class QACreate(BaseModel):
    writer: str
    email: Optional[EmailStr] = None
    password: str
    title: str
    content: Optional[str] = None
    hidden: bool = False
    qa_type: QAType = QAType.CUSTOMER


class QARetrieve(BaseModel):
    id: int
    writer: str
    email: Optional[str]
    title: str
    content: Optional[str]
    c_date: Optional[str]
    done: bool
    read_cnt: int
    hidden: bool
    qa_type: QAType
    attachment_filename: Optional[str] = None  # Add filename field

    class Config:
        from_attributes = True
