from typing import Optional

from pydantic import EmailStr, BaseModel
from sqlmodel import SQLModel, Field

from models.answers import Answer


class BusScheduleBase(SQLModel):
    title: str
    image_data: Optional[bytes] = None
    image_name: Optional[str] = None


class BusSchedule(BusScheduleBase, table=True):
    __tablename__ = 'bus_schedule'
    id: int = Field(primary_key=True, default=None)


class QAShort(SQLModel):
    id: int


class BusSchedulePublic(BusScheduleBase):
    id: int
    attachment: Optional[str] = None  # Base64 인코딩된 문자열로 변환


class BusScheduleWithAnswer(BusSchedulePublic):
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
