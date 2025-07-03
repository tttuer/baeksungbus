from typing import Optional

from pydantic import EmailStr, BaseModel
from sqlmodel import SQLModel, Field


class BusScheduleBase(SQLModel):
    title: str
    image_data1: Optional[bytes] = None
    image_name1: Optional[str] = None
    image_data2: Optional[bytes] = None
    image_name2: Optional[str] = None
    image_data3: Optional[bytes] = None
    image_name3: Optional[str] = None


class BusSchedule(BusScheduleBase, table=True):
    __tablename__ = 'bus_schedule'
    id: int = Field(primary_key=True, default=None)


class QAShort(SQLModel):
    id: int


class BusSchedulePublic(BaseModel):
    id: int
    image_name1: Optional[str] = None  # Base64 인코딩된 문자열로 변환
    image_name2: Optional[str] = None  # Base64 인코딩된 문자열로 변환
    image_name3: Optional[str] = None  # Base64 인코딩된 문자열로 변환
    image_data1: Optional[str] = None  # Base64 인코딩된 문자열로 변환
    image_data2: Optional[str] = None  # Base64 인코딩된 문자열로 변환
    image_data3: Optional[str] = None  # Base64 인코딩된 문자열로 변환
    title: Optional[str] = None


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
    attachment_filename: Optional[str] = None  # Add filename field

    class Config:
        from_attributes = True
